/**
 * 响应拦截器管理器
 * - 负责在成功解析响应数据之后，执行用户注册的响应拦截器
 * - 支持 onRejected：在请求抛错或解析失败时统一处理错误（如登录过期、全局提示等）
 */
import type { RequestContext } from "./types"

export type ResponseFulfilledFn<T = any> = (
  data: T,
  response: Response,
  ctx: RequestContext
) => Promise<T> | T
export type ResponseRejectedFn = (
  error: unknown,
  response?: Response,
  ctx?: RequestContext
) => Promise<never> | never

class ResponseInterceptorManager<T = any> {
  private readonly handlers = new Map<
    number,
    { onFulfilled: ResponseFulfilledFn<T>; onRejected?: ResponseRejectedFn }
  >()
  private idSeq = 0

  use(
    onFulfilled: ResponseFulfilledFn<T>,
    onRejected?: ResponseRejectedFn
  ): number {
    const id = ++this.idSeq
    this.handlers.set(id, { onFulfilled, onRejected })
    return id
  }

  eject(id: number): void {
    this.handlers.delete(id)
  }

  async run(data: T, response: Response, ctx: RequestContext): Promise<T> {
    let result = data
    for (const { onFulfilled } of this.handlers.values()) {
      result = await onFulfilled(result, response, ctx)
    }
    return result
  }

  /**
   * 依次调用所有注册的 onRejected，用于统一错误处理
   * 约定：onRejected 应当抛出错误（或返回 rejected promise）以中断后续链路
   */
  async runRejected(
    error: unknown,
    response?: Response,
    ctx?: RequestContext
  ): Promise<never> {
    for (const { onRejected } of this.handlers.values()) {
      if (onRejected) {
        await onRejected(error, response, ctx)
      }
    }
    // 如果所有 onRejected 都未抛错，则在此统一抛出原始错误
    throw error as any
  }
}

export const responseInterceptors = new ResponseInterceptorManager()
