/*
  通用请求与拦截器类型定义
*/

import type { AxiosResponse, Method, InternalAxiosRequestConfig } from "axios"

// 后端统一响应格式
export interface ApiResponse<T = unknown> {
  code: number
  msg: string
  data: T
}

// 统一错误对象
export class RequestError<T = unknown> extends Error {
  public readonly name = "RequestError"
  public readonly status?: number
  public readonly code?: number
  public readonly details?: T
  public readonly isNetworkError: boolean
  public readonly isTimeout: boolean

  constructor(options: {
    message: string
    status?: number
    code?: number
    details?: T
    isNetworkError?: boolean
    isTimeout?: boolean
  }) {
    super(options.message)
    this.status = options.status
    this.code = options.code
    this.details = options.details
    this.isNetworkError = Boolean(options.isNetworkError)
    this.isTimeout = Boolean(options.isTimeout)
  }
}

// 生成请求键的输入
export interface RequestKeyParts {
  method: Method | string | undefined
  url: string | undefined
  params?: unknown
  data?: unknown
  headers?: Record<string, unknown> | undefined
}

// 自定义扩展配置
export interface ExtraRequestOptions {
  // 是否注入认证头
  withAuth?: boolean
  // 是否将后端统一响应格式转为 data，否则返回原始响应
  transformResponse?: boolean
  // 是否防止重复请求（基于请求键）
  preventDuplicate?: boolean
  // 自定义请求键（不传则使用 method+url+params+data）
  cancelKey?: string
  // 传入外部 AbortSignal，以便外部控制取消
  signal?: AbortSignal
}

export type RequestConfig<T = unknown> = InternalAxiosRequestConfig<T> &
  ExtraRequestOptions

export interface CreateClientOptions {
  baseURL?: string
  timeout?: number
  defaultHeaders?: Record<string, string>
  // 未授权统一处理回调（例如跳转登录）
  onUnauthorized?: () => void
}

export interface PendingRequestRecord {
  controller: AbortController
  timestamp: number
}

export type AxiosSuccess<T = unknown> = AxiosResponse<T>
