import { buildUrlWithParams, normalizeRequestBody } from "./paramFormatter"
import { pendingManager } from "./pendingManager"
import { requestInterceptors } from "./requestInterceptor"
import { responseInterceptors } from "./responseInterceptor"
import { buildRequestKey } from "./requestKey"
import type {
  ApiResponseEnvelope,
  HttpMethod,
  RequestContext,
  RequestOptions,
} from "./types"
import { HttpError } from "./types"

const DEFAULT_TIMEOUT = 15000 // 15s

async function parseJsonSafe(response: Response): Promise<any | undefined> {
  const ct = response.headers.get("content-type") || ""
  if (ct.includes("application/json")) {
    try {
      return await response.json()
    } catch {
      return undefined
    }
  }
  return undefined
}

/**
 * 统一响应解析：
 * - 非 rawResponse：尝试解析统一业务包裹 { code, msg, data }
 * - rawResponse：直接返回原生 Response
 * - 非 2xx 状态码：抛出 HttpError
 */
async function handleResponse<T>(
  response: Response,
  ctx: RequestContext
): Promise<T> {
  if (ctx.rawResponse) {
    return response as unknown as T
  }
  const parsed = (await parseJsonSafe(response)) as
    | ApiResponseEnvelope<T>
    | undefined
  if (!response.ok) {
    throw new HttpError(`HTTP ${response.status} ${response.statusText}`, {
      status: response.status,
      statusText: response.statusText,
      data: parsed,
      url: ctx.url,
    })
  }
  if (ctx.noValidateEnvelope) {
    return (parsed as unknown as T) ?? ({} as T)
  }
  if (!parsed || typeof parsed.code !== "number") {
    throw new HttpError("Invalid API envelope", {
      status: response.status,
      statusText: response.statusText,
      data: parsed,
      url: ctx.url,
    })
  }
  if (parsed.code !== 0) {
    throw new HttpError(parsed.msg || "API Error", {
      status: response.status,
      statusText: response.statusText,
      data: parsed,
      url: ctx.url,
    })
  }
  return parsed.data as T
}

function withTimeout(
  signal: AbortSignal | undefined,
  ms: number
): AbortSignal | undefined {
  if (ms <= 0) return signal
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), ms)
  if (signal) {
    signal.addEventListener("abort", () => controller.abort(), { once: true })
  }
  // Ensure timeout cleared when aborted externally
  controller.signal.addEventListener("abort", () => clearTimeout(timeoutId), {
    once: true,
  })
  return controller.signal
}

async function coreFetch<T>(
  url: string,
  options: RequestOptions = {}
): Promise<T> {
  const fetchImpl = options.fetchImpl ?? fetch
  const method: HttpMethod = (
    options.method ?? "GET"
  ).toUpperCase() as HttpMethod
  const headers: Record<string, string> = { ...(options.headers || {}) }
  let ctx: RequestContext = {
    url,
    method,
    headers,
    params: options.params,
    body: options.body,
    timeoutMs: options.timeoutMs ?? DEFAULT_TIMEOUT,
    cancelKey: options.cancelKey,
    dedupe: options.dedupe ?? true,
    cancelPrevious: options.cancelPrevious ?? false,
    rawResponse: options.rawResponse ?? false,
    noValidateEnvelope: options.noValidateEnvelope ?? false,
    fetchImpl,
    signal: options.signal,
  }

  ctx = await requestInterceptors.run(ctx)

  const key = ctx.cancelKey
    ? buildRequestKey({
        method: ctx.method,
        url: ctx.url,
        params: ctx.params,
        body: ctx.body,
      })
    : undefined
  if (ctx.dedupe && key) {
    const existing = pendingManager.getPromise<T>(key)
    if (existing) return existing
  }

  const finalUrl = buildUrlWithParams(ctx.url, ctx.params)
  const body =
    ctx.method === "GET" || ctx.method === "HEAD"
      ? undefined
      : normalizeRequestBody(ctx.body, ctx.headers)

  const internalSignal = pendingManager.attachController(ctx)
  const combinedSignal = withTimeout(
    internalSignal ?? ctx.signal,
    ctx.timeoutMs
  )

  const p = (async () => {
    try {
      const response = await (ctx.fetchImpl ?? fetch)(finalUrl, {
        method: ctx.method,
        headers: ctx.headers,
        body,
        signal: combinedSignal,
      })
      let data = await handleResponse<T>(response, ctx)
      data = await responseInterceptors.run(data, response, ctx)
      return data
    } catch (error: any) {
      // 将错误透传给响应拦截器的 onRejected（如果有注册），并确保最终抛出错误
      await responseInterceptors.runRejected(error)
      throw error
    }
  })().finally(() => {
    if (key) pendingManager.clear(key)
  })

  if (ctx.dedupe && key) pendingManager.setPromise(key, p)
  return p
}

export const request = Object.assign(coreFetch, {
  get: <T>(
    url: string,
    options: Omit<RequestOptions, "method" | "body"> = {}
  ) => coreFetch<T>(url, { ...options, method: "GET" }),
  delete: <T>(
    url: string,
    options: Omit<RequestOptions, "method" | "body"> = {}
  ) => coreFetch<T>(url, { ...options, method: "DELETE" }),
  post: <T>(
    url: string,
    body?: unknown,
    options: Omit<RequestOptions, "method" | "body"> = {}
  ) => coreFetch<T>(url, { ...options, method: "POST", body }),
  put: <T>(
    url: string,
    body?: unknown,
    options: Omit<RequestOptions, "method" | "body"> = {}
  ) => coreFetch<T>(url, { ...options, method: "PUT", body }),
  patch: <T>(
    url: string,
    body?: unknown,
    options: Omit<RequestOptions, "method" | "body"> = {}
  ) => coreFetch<T>(url, { ...options, method: "PATCH", body }),
  // 返回原始 Response，可用于流式传输
  stream: (url: string, options: Omit<RequestOptions, "rawResponse"> = {}) =>
    coreFetch<Response>(url, { ...options, rawResponse: true }),
})

export type { RequestOptions }
export { requestInterceptors, responseInterceptors, HttpError }
