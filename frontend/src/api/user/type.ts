/** 登录凭证 */
export interface LoginCredentials {
  username: string
  password: string
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string
  token_type: string
}

/** 注册凭证 */
export interface RegisterCredentials {
  email: string
  password: string
  full_name: string
  avatar_url: string
  bio: string
  location: string
  website: string
  gender: "male" | "female" | "other"
}
