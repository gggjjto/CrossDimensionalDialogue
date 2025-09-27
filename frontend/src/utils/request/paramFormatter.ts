/**
 * 构建 URL 并添加查询字符串参数
 * @param url 原始 URL
 * @param params 查询字符串参数
 * @returns 构建后的 URL
 */
export function buildUrlWithParams(
  url: string,
  params?: Record<string, unknown>
): string {
  if (!params || Object.keys(params).length === 0) return url
  const usp = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) continue
    if (Array.isArray(value)) {
      for (const v of value) usp.append(key, String(v))
    } else if (typeof value === "object") {
      usp.set(key, JSON.stringify(value))
    } else {
      usp.set(key, String(value))
    }
  }
  const joiner = url.includes("?") ? "&" : "?"
  return `${url}${joiner}${usp.toString()}`
}

/**
 * 规范化请求体
 * @param body 请求体
 * @param headers 请求头
 * @returns 规范化后的请求体
 */
export function normalizeRequestBody(
  body: unknown,
  headers: Record<string, string>
): BodyInit | undefined {
  if (body === undefined || body === null) return undefined
  // 若为 FormData，直接返回，且不要主动设置 Content-Type（让浏览器带上 multipart 边界）
  if (typeof FormData !== "undefined" && body instanceof FormData) {
    return body as unknown as BodyInit
  }
  const contentType = Object.keys(headers).find(
    (k) => k.toLowerCase() === "content-type"
  )
  const ct = contentType ? headers[contentType] : undefined
  if (!ct) {
    headers["Content-Type"] = "application/json"
    return JSON.stringify(body)
  }
  if (ct.includes("application/json")) {
    return typeof body === "string" ? (body as string) : JSON.stringify(body)
  }
  if (ct.includes("application/x-www-form-urlencoded")) {
    const usp = new URLSearchParams()
    Object.entries(body as Record<string, unknown>).forEach(([k, v]) => {
      if (v === undefined || v === null) return
      usp.set(k, String(v))
    })
    return usp as unknown as BodyInit
  }
  // 对于 multipart/form-data，boundary 必须由浏览器自动设置；如果手动设置了，则假定 body 已经是 FormData 或已编码
  return body as BodyInit
}
