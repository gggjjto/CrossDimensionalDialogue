import axios from "axios"
import type { AxiosInstance } from "axios"
import { onRequest, setTokenGetter } from "./requestInterceptor"
import {
  onResponse,
  onResponseError,
  setUnauthorizedHandler,
} from "./responseInterceptor"
import type { CreateClientOptions, RequestConfig } from "./types"
import { pendingRequestManager } from "./pendingManager"

const DEFAULT_TIMEOUT = 15000

function createAxiosClient(options: CreateClientOptions = {}): AxiosInstance {
  const instance = axios.create({
    baseURL: options.baseURL || "/api",
    timeout: options.timeout ?? DEFAULT_TIMEOUT,
    headers: {
      "Content-Type": "application/json",
      ...(options.defaultHeaders || {}),
    },
  })

  // 注入 401 处理
  setUnauthorizedHandler(options.onUnauthorized)

  // 注册拦截器
  instance.interceptors.request.use(onRequest)
  instance.interceptors.response.use(onResponse, onResponseError)

  return instance
}

// 提供默认客户端
export const httpClient = createAxiosClient()

// 允许外部设置获取 token 方法
export { setTokenGetter }

// 取消所有请求能力
export function cancelAllRequests(reason?: string) {
  pendingRequestManager.cancelAll(reason)
}

// 便捷方法，带类型
export function get<T = unknown>(url: string, config?: RequestConfig) {
  return httpClient.get<T>(url, config as any)
}

export function post<T = unknown>(
  url: string,
  data?: unknown,
  config?: RequestConfig
) {
  return httpClient.post<T>(url, data, config as any)
}

export function put<T = unknown>(
  url: string,
  data?: unknown,
  config?: RequestConfig
) {
  return httpClient.put<T>(url, data, config as any)
}

export function del<T = unknown>(url: string, config?: RequestConfig) {
  return httpClient.delete<T>(url, config as any)
}

// 导出创建自定义实例的能力，便于多后端/多服务场景
export function createHttpClient(options?: CreateClientOptions) {
  return createAxiosClient(options)
}

export type { RequestConfig } from "./types"
