/*
  请求参数格式化工具：
  - 移除 undefined
  - 将 Date 转为 ISO 字符串
  - 可选地将 null 移除或保留
*/

export interface NormalizeOptions {
  removeNull?: boolean
}

export function normalizeParams<T extends unknown>(
  input: T,
  options: NormalizeOptions = {}
): T {
  const { removeNull = false } = options

  const recur = (val: unknown): unknown => {
    if (val === undefined) return undefined
    if (val === null) return removeNull ? undefined : null
    if (val instanceof Date) return val.toISOString()

    if (Array.isArray(val)) {
      const arr = (val as unknown[])
        .map((item) => recur(item))
        .filter((v) => v !== undefined)
      return arr as unknown
    }

    if (typeof val === "object") {
      const obj = val as Record<string, unknown>
      const out: Record<string, unknown> = {}
      for (const key of Object.keys(obj)) {
        const v = recur(obj[key])
        if (v !== undefined) out[key] = v
      }
      return out
    }

    return val
  }

  return recur(input) as T
}
