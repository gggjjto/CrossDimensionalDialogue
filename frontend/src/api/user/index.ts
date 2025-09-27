import { request } from "@/utils/request"
import { LoginCredentials, LoginResponse, RegisterCredentials } from "./type"

export const userApi = {
  /** 登录 */
  login: async (body: LoginCredentials) => {
    return request.post<LoginResponse>(
      "/v1/login/access-token-v2",
      {
        ...body,
        grant_type: "password",
        // 对齐后端 OAuth2 表单字段，避免 422
        scope: "",
        client_id: "string",
        client_secret: "string",
      },
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    )
  },
  /** 获取当前用户信息 */
  me: async () => {
    return request.get<any>('/v1/users/me')
  },
  /** 更新当前用户信息 */
  updateMe: async (body: Partial<{ full_name: string; email: string; avatar_url: string; bio: string; gender: 'male' | 'female' | 'other' }>) => {
    return request.patch<any>('/v1/users/me', body)
  },
  /** 注册 */
  register: async (body: RegisterCredentials) => {
    return request.post("/v1/users/signup", body)
  },
}
