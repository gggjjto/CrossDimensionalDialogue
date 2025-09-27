import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"

import { request } from "@/utils/request"
import { userApi } from "@/api/user"
import type {
  CurrentUser,
  LoginCredentials,
  LoginResponse,
  RegisterCredentials,
} from "@/api/user/type"

// 检查是否已登录
export function isLoggedIn(): boolean {
  const token = localStorage.getItem("access_token")
  return !!token
}

export default function useAuth() {
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  // 获取当前用户信息
  const { data: user } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async (): Promise<CurrentUser> => {
      const data = await request.get<CurrentUser>("/v1/users/me")
      return data
    },
    enabled: isLoggedIn(),
  })

  // 登录
  const loginMutation = useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const payload: LoginCredentials = {
        username: credentials.email,
        password: credentials.password,
      }
      const res: LoginResponse = await userApi.login(payload)
      return res
    },
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("token_type", data.token_type)
      setError(null)
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: "/" })
    },
    onError: (err: any) => {
      setError(err?.message || "登录失败，请检查用户名和密码")
    },
  })

  // 注册（成功后自动登录并跳转）
  const registerMutation = useMutation({
    mutationFn: async (payload: RegisterCredentials) => {
      await userApi.register(payload)
      // 注册后自动登录
      const loginRes = await userApi.login({
        username: payload.email,
        password: payload.password,
      })
      return loginRes
    },
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("token_type", data.token_type)
      setError(null)
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: "/" })
    },
    onError: (err: any) => {
      setError(err?.message || "注册失败，请检查输入信息")
    },
  })

  const logout = async () => {
    try {
      // 清除本地存储
      localStorage.removeItem("access_token")
      localStorage.removeItem("token_type")
      // 清除查询缓存
      queryClient.clear()
      // 跳转登录
      navigate({ to: "/login" })
    } catch (error) {
      // no-op
    }
  }

  const resetError = () => setError(null)

  return {
    user,
    error,
    loginMutation,
    registerMutation,
    logout,
    resetError,
    isLoading: loginMutation.isPending,
  }
}
