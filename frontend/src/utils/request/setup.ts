/**
 * 请求模块统一初始化
 * - 统一基础 baseUrl
 * - 统一请求头（Accept、Authorization 等）
 * 使用方式：在应用入口（如 main.tsx）顶部导入一次：
 *   import "@/utils/request/setup"
 */
import { requestInterceptors } from "@/utils/request"

requestInterceptors.use((ctx) => {
  // 1) 统一基础 baseUrl（仅在传入相对路径时拼接）
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api"
  if (!/^https?:\/\//i.test(ctx.url)) {
    ctx.url = `${baseUrl.replace(/\/+$/, "")}/${ctx.url.replace(/^\/+/, "")}`
  }

  // 2) 统一请求头
  const headers = ctx.headers || {}
  if (!headers.Accept) headers.Accept = "application/json"

  const token = localStorage.getItem("access_token")
  if (token && !headers.Authorization) {
    headers.Authorization = `Bearer ${token}`
  }

  ctx.headers = headers
  return ctx
})
