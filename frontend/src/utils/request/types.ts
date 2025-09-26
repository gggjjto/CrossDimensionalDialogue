/**
 * 通用请求与响应类型定义
 * - 定义 HTTP 方法、请求可选项、请求上下文
 * - 定义统一响应包裹类型与 HttpError 错误类型
 * - 提供拦截器管理器的类型接口
 */
export type HttpMethod =
  | "GET"
  | "POST"
  | "PUT"
  | "DELETE"
  | "PATCH"
  | "HEAD"
  | "OPTIONS"

export interface ApiResponseEnvelope<T = unknown> {
  /** 业务状态码：0 表示成功，非 0 表示失败 */
  code: number
  /** 业务消息：成功或错误信息 */
  msg: string
  /** 业务数据载荷 */
  data: T
}

export interface RequestOptions<TBody = unknown> {
  /** HTTP 方法，默认 GET */
  method?: HttpMethod
  /** 额外请求头 */
  headers?: Record<string, string>
  /** 查询字符串参数，会自动格式化并拼接到 URL */
  params?: Record<string, unknown>
  /** 请求体（会根据 Content-Type 进行规范化） */
  body?: TBody
  /** 超时时间，单位毫秒，默认 15000ms */
  timeoutMs?: number
  /** 自定义取消/去重键，不传则自动基于 method+url+params+body 生成 */
  cancelKey?: string
  /**
   * 避免发送重复的请求，如果 true，后续的请求会返回相同的 promise 直到 resolved。
   */
  dedupe?: boolean
  /**
   * 如果 true，当新的请求与相同的键被发出时，前面的请求会被取消。
   */
  cancelPrevious?: boolean
  /**
   * 如果 true，不解包 API 响应包裹并返回原始 Response。
   */
  rawResponse?: boolean
  /**
   * 如果 true，不解包 API 响应包裹并返回原始 Response。
   */
  noValidateEnvelope?: boolean
  /**
   * 自定义 fetch 实现（例如，同构或包装的）。
   */
  fetchImpl?: typeof fetch
  /** 传递一个外部 AbortSignal 来控制取消 */
  signal?: AbortSignal
}

export interface RequestContext<TBody = unknown>
  extends Required<Pick<RequestOptions<TBody>, "method">> {
  /** 原始 URL（不包含查询字符串） */
  url: string
  /** 请求头，已合并默认与用户设置 */
  headers: Record<string, string>
  /** 查询字符串参数 */
  params?: Record<string, unknown>
  /** 请求体 */
  body?: TBody
  /** 超时时间（毫秒） */
  timeoutMs: number
  /** 取消/去重键 */
  cancelKey?: string
  /** 是否对相同键的请求进行去重 */
  dedupe: boolean
  /** 是否触发后来的请求取消先前的同键请求 */
  cancelPrevious: boolean
  /** 是否直接返回原生 Response */
  rawResponse: boolean
  /** 是否跳过对统一响应包裹结构的校验 */
  noValidateEnvelope: boolean
  /** 自定义 fetch 实现 */
  fetchImpl?: typeof fetch
  /** 外部传入的取消信号 */
  signal?: AbortSignal
}

export interface RequestInterceptor {
  (
    onFulfilled: (
      ctx: RequestContext
    ) => Promise<RequestContext> | RequestContext,
    onRejected?: (error: unknown) => Promise<never> | never
  ): number
}

export interface ResponseHandler<T = unknown> {
  (response: Response, ctx: RequestContext): Promise<T>
}

export interface ResponseInterceptor<T = unknown> {
  (
    onFulfilled: (
      data: T,
      response: Response,
      ctx: RequestContext
    ) => Promise<T> | T,
    onRejected?: (
      error: unknown,
      response?: Response,
      ctx?: RequestContext
    ) => Promise<never> | never
  ): number
}

export class HttpError<T = any> extends Error {
  public status: number
  public statusText: string
  public data?: T
  public url?: string

  constructor(
    message: string,
    init: { status: number; statusText: string; data?: T; url?: string }
  ) {
    super(message)
    this.name = "HttpError"
    this.status = init.status
    this.statusText = init.statusText
    this.data = init.data
    this.url = init.url
  }
}

export interface InterceptorManager<TArgs extends any[]> {
  use(
    onFulfilled: (...args: TArgs) => any,
    onRejected?: (...args: any[]) => any
  ): number
  eject(id: number): void
}
