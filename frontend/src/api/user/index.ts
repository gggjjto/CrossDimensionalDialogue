import { request } from "@/utils/request"
import { LoginCredentials, LoginResponse, RegisterCredentials } from "./type"

export const userApi = {
  /** 登录 */
  login: async (body: LoginCredentials) => {
    return request.post<LoginResponse>("/api/v1/login/access-token-v2", {
      ...body,
      grant_type: "password",
    })
  },
  /** 注册 */
  register: async (body: RegisterCredentials) => {
    return request.post("/api/v1/users/signup", body)
  },
}
