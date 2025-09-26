export function buildUrlWithParams(
  url: string,
  params?: Record<string, unknown>
): string {
  if (!params || Object.keys(params).length === 0) return url
  const usp = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) continue
    if (Array.isArray(value)) {
      for (const v of value) usp.append(key, String(v))
    } else if (typeof value === "object") {
      usp.set(key, JSON.stringify(value))
    } else {
      usp.set(key, String(value))
    }
  }
  const joiner = url.includes("?") ? "&" : "?"
  return `${url}${joiner}${usp.toString()}`
}

export function normalizeRequestBody(
  body: unknown,
  headers: Record<string, string>
): BodyInit | undefined {
  if (body === undefined || body === null) return undefined
  const contentType = Object.keys(headers).find(
    (k) => k.toLowerCase() === "content-type"
  )
  const ct = contentType ? headers[contentType] : undefined
  if (!ct) {
    // Default to JSON
    headers["Content-Type"] = "application/json"
    return JSON.stringify(body)
  }
  if (ct.includes("application/json")) {
    return typeof body === "string" ? (body as string) : JSON.stringify(body)
  }
  if (ct.includes("application/x-www-form-urlencoded")) {
    const usp = new URLSearchParams()
    Object.entries(body as Record<string, unknown>).forEach(([k, v]) => {
      if (v === undefined || v === null) return
      usp.set(k, String(v))
    })
    return usp as unknown as BodyInit
  }
  // For multipart/form-data the boundary must be set by the browser; if user set it manually, assume body is FormData or already encoded
  return body as BodyInit
}
