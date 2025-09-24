import type { AxiosError, AxiosResponse } from "axios"
import { pendingRequestManager } from "./pendingManager"
import type { ApiResponse, RequestConfig } from "./types"
import { buildRequestKey } from "./requestKey"
import { RequestError } from "./types"

// 未授权回调，由主入口注入
let onUnauthorized: (() => void) | undefined
export function setUnauthorizedHandler(handler?: () => void) {
  onUnauthorized = handler
}

export function onResponse(response: AxiosResponse): any {
  const cfg = response.config as RequestConfig
  // 清理 pending
  const key =
    cfg.cancelKey ||
    buildRequestKey({
      method: cfg.method,
      url: cfg.url,
      params: cfg.params,
      data: cfg.data,
    })
  pendingRequestManager.remove(key)

  // 统一转化
  const shouldTransform = cfg.transformResponse !== false
  if (!shouldTransform) return response

  const payload = response.data as ApiResponse
  // 若后端非统一格式，直接返回 data
  if (
    payload &&
    typeof payload === "object" &&
    "code" in payload &&
    "data" in payload
  ) {
    if (payload.code === 0) {
      return payload.data
    }
    // 后端错误码
    throw new RequestError({
      message: payload.msg || "请求失败",
      code: payload.code,
      status: response.status,
      details: payload.data,
    })
  }

  return response.data
}

export function onResponseError(error: AxiosError): never {
  const cfg = (error.config || {}) as RequestConfig

  // 清理 pending
  if (cfg.url) {
    const key =
      cfg.cancelKey ||
      buildRequestKey({
        method: cfg.method,
        url: cfg.url,
        params: cfg.params,
        data: cfg.data,
      })
    pendingRequestManager.remove(key)
  }

  // 取消请求
  if (error.code === "ERR_CANCELED") {
    throw new RequestError({ message: "请求已取消", isNetworkError: false })
  }

  // 网络错误/超时
  if (!error.response) {
    const isTimeout = (error as any).code === "ECONNABORTED"
    throw new RequestError({
      message: isTimeout ? "请求超时" : "网络错误",
      isNetworkError: !isTimeout,
      isTimeout,
    })
  }

  const status = error.response.status
  const data = error.response.data as any

  if (status === 401 && onUnauthorized) {
    onUnauthorized()
  }

  // 后端统一结构错误
  if (data && typeof data === "object" && "code" in data && "msg" in data) {
    throw new RequestError({
      message: data.msg || "请求失败",
      status,
      code: data.code,
      details: data.data,
    })
  }

  throw new RequestError({ message: error.message, status })
}
