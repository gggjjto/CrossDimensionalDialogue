import type { InternalAxiosRequestConfig, AxiosHeaders } from "axios"
import { normalizeParams } from "./paramFormatter"
import type { RequestConfig } from "./types"
import { pendingRequestManager } from "./pendingManager"

// 默认获取token的方法，允许在外部替换注入
let getToken: () => string | null = () => {
  try {
    return localStorage.getItem("access_token")
  } catch {
    return null
  }
}

export function setTokenGetter(fn: () => string | null) {
  getToken = fn
}

export function onRequest(
  config: InternalAxiosRequestConfig
): InternalAxiosRequestConfig {
  const cfg = config as RequestConfig

  // 参数格式化
  if (cfg.params) cfg.params = normalizeParams(cfg.params)
  if (cfg.data && typeof cfg.data === "object")
    cfg.data = normalizeParams(cfg.data)

  // 注入认证头
  if (cfg.withAuth !== false) {
    const token = getToken()
    if (token) {
      const headers = cfg.headers as AxiosHeaders | Record<string, string>
      if (typeof (headers as any).set === "function") {
        ;(headers as any).set("Authorization", `Bearer ${token}`)
      } else {
        ;(headers as Record<string, string>)[
          "Authorization"
        ] = `Bearer ${token}`
      }
    }
  }

  // 去重与取消：仅当 preventDuplicate !== false 时生效
  if (cfg.preventDuplicate !== false) {
    pendingRequestManager.add(cfg)
  }

  return cfg
}
