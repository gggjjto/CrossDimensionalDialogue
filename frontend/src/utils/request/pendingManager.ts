import type { PendingRequestRecord, RequestConfig } from "./types"
import { buildRequestKey } from "./requestKey"

// 管理挂起请求：支持去重与取消
export class PendingRequestManager {
  private readonly map = new Map<string, PendingRequestRecord>()

  public add(config: RequestConfig): string {
    const key =
      config.cancelKey ||
      buildRequestKey({
        method: config.method,
        url: config.url,
        params: config.params,
        data: config.data,
      })

    if (this.map.has(key)) {
      // 已有相同请求，取消新请求
      const existing = this.map.get(key)!
      existing.controller.abort("duplicate-request")
      this.map.delete(key)
    }

    const controller = new AbortController()
    this.map.set(key, {
      controller,
      timestamp: Date.now(),
    })

    // 将 signal 合并到 config
    config.signal = config.signal ?? controller.signal

    return key
  }

  public remove(key: string): void {
    const record = this.map.get(key)
    if (!record) return
    this.map.delete(key)
  }

  public cancel(key: string, reason?: string): void {
    const record = this.map.get(key)
    if (!record) return
    record.controller.abort(reason)
    this.map.delete(key)
  }

  public cancelAll(reason?: string): void {
    for (const [key, record] of this.map) {
      record.controller.abort(reason)
      this.map.delete(key)
    }
  }
}

export const pendingRequestManager = new PendingRequestManager()
