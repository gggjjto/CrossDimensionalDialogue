import { buildRequestKey } from "./requestKey"
import type { RequestContext } from "./types"

export class PendingManager {
  private readonly keyToController = new Map<string, AbortController>()
  private readonly keyToPromise = new Map<string, Promise<any>>()

  createKey(ctx: RequestContext): string {
    // Use user-provided key if present; otherwise derive a stable key from request parts
    if (ctx.cancelKey) return ctx.cancelKey
    return buildRequestKey({
      method: ctx.method,
      url: ctx.url,
      params: ctx.params,
      body: ctx.body,
    })
  }

  getPromise<T = any>(key?: string): Promise<T> | undefined {
    if (!key) return undefined
    return this.keyToPromise.get(key) as Promise<T> | undefined
  }

  setPromise(key: string, promise: Promise<any>): void {
    this.keyToPromise.set(key, promise)
    promise.finally(() => {
      this.keyToPromise.delete(key)
    })
  }

  attachController(ctx: RequestContext): AbortSignal | undefined {
    const key = this.createKey(ctx)
    if (ctx.cancelPrevious) {
      this.abort(key)
    }
    const controller = new AbortController()
    this.keyToController.set(key, controller)
    return controller.signal
  }

  abort(key: string): void {
    const controller = this.keyToController.get(key)
    if (controller) {
      controller.abort()
      this.keyToController.delete(key)
    }
  }

  clear(key: string | undefined): void {
    if (!key) return
    this.keyToController.delete(key)
  }
}

export const pendingManager = new PendingManager()
