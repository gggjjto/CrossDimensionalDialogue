/**
 * 请求拦截器管理器
 * - 在真正发起 fetch 之前，允许统一修改请求上下文
 * - 常见用途：基础 baseUrl、统一请求头、鉴权 Token、追踪 ID 等
 */
import type { RequestContext } from "./types"

export type RequestInterceptorFn = (
  ctx: RequestContext
) => Promise<RequestContext> | RequestContext

class RequestInterceptorManager {
  private readonly handlers = new Map<
    number,
    { onFulfilled: RequestInterceptorFn; onRejected?: (error: unknown) => any }
  >()
  private idSeq = 0

  use(
    onFulfilled: RequestInterceptorFn,
    onRejected?: (error: unknown) => any
  ): number {
    const id = ++this.idSeq
    this.handlers.set(id, { onFulfilled, onRejected })
    return id
  }

  eject(id: number): void {
    this.handlers.delete(id)
  }

  async run(ctx: RequestContext): Promise<RequestContext> {
    let result = ctx
    for (const { onFulfilled } of this.handlers.values()) {
      result = await onFulfilled(result)
    }
    return result
  }
}

export const requestInterceptors = new RequestInterceptorManager()
