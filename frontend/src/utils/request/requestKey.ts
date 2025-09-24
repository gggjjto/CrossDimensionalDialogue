import type { RequestKeyParts } from "./types"

// 稳定字符串化
function stableStringify(value: unknown): string {
  const seen = new WeakSet<object>()

  const helper = (val: unknown): unknown => {
    if (val === null || typeof val !== "object") {
      if (val instanceof Date) return val.toISOString()
      return val
    }

    if (seen.has(val as object)) {
      return "[Circular]"
    }
    seen.add(val as object)

    if (Array.isArray(val)) {
      return (val as unknown[]).map((item) => helper(item))
    }

    const obj = val as Record<string, unknown>
    const keys = Object.keys(obj).sort()
    const sorted: Record<string, unknown> = {}
    for (const key of keys) {
      const v = obj[key]
      if (v === undefined) continue
      sorted[key] = helper(v)
    }
    return sorted
  }

  return JSON.stringify(helper(value))
}

// 构建请求键
export function buildRequestKey(parts: RequestKeyParts): string {
  const method = (parts.method || "GET").toString().toUpperCase()
  const url = parts.url || ""
  const params = parts.params ? stableStringify(parts.params) : ""
  const data = parts.data ? stableStringify(parts.data) : ""
  return `${method}|${url}|p:${params}|d:${data}`
}
