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

/** 注册凭证（与后端 UserRegister 对齐） */
export interface RegisterCredentials {
  email: string
  password: string
  full_name?: string
  avatar_url?: string
  bio?: string
  location?: string
  website?: string
  gender?: "male" | "female" | "other" | "prefer_not_to_say"
}

/** 当前用户信息（后端 UserPublic 的子集） */
export interface CurrentUser {
  id: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  character_count?: number
  conversation_count?: number
}
