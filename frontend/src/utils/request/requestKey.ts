/**
 * 构建请求唯一键（用于去重与取消）
 * - 通过稳定序列化 method/url/params/body 得到稳定键
 */
import type { HttpMethod } from "./types"

export interface RequestKeyParts {
  method: HttpMethod
  url: string
  params?: Record<string, unknown>
  body?: unknown
}

/** 稳定序列化，确保对象/数组键顺序不影响结果 */
function stableStringify(value: unknown): string {
  if (value === undefined) return ""
  if (value === null) return "null"
  if (typeof value !== "object") return String(value)
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`
  const obj = value as Record<string, unknown>
  const keys = Object.keys(obj).sort()
  return `{${keys.map((k) => `${k}:${stableStringify(obj[k])}`).join(",")}}`
}

/**
 * 生成请求键
 */
export function buildRequestKey(parts: RequestKeyParts): string {
  const { method, url, params, body } = parts
  return `${method} ${url} | p:${stableStringify(params)} | b:${stableStringify(
    body
  )}`
}
