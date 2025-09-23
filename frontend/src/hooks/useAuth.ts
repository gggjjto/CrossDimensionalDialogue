import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"

// TODO: 根据实际后端API调整这些类型
interface User {
  id: number
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
}

interface LoginCredentials {
  username: string
  password: string
}

interface AuthResponse {
  access_token: string
  token_type: string
}

// 临时的认证API - 您可以替换为实际的API调用
const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    // TODO: 替换为实际的登录API调用
    console.log("Login attempt:", credentials)
    return {
      access_token: "fake-token",
      token_type: "bearer",
    }
  },

  getCurrentUser: async (): Promise<User> => {
    // TODO: 替换为实际的获取当前用户API调用
    return {
      id: 1,
      email: "test@example.com",
      full_name: "Test User",
      is_active: true,
      is_superuser: false,
    }
  },

  logout: async (): Promise<void> => {
    // TODO: 实现登出逻辑
    console.log("Logout")
  },
}

// 检查是否已登录的辅助函数
export function isLoggedIn(): boolean {
  // TODO: 实现真正的登录状态检查逻辑
  // 可以检查 localStorage 中的 token 或其他状态
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
    queryFn: authAPI.getCurrentUser,
    enabled: isLoggedIn(), // 只有在已登录时才获取用户信息
  })

  // 登录mutation
  const loginMutation = useMutation({
    mutationFn: authAPI.login,
    onSuccess: (data) => {
      // 保存token到localStorage
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("token_type", data.token_type)

      // 清除错误状态
      setError(null)

      // 重新获取用户信息
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })

      // 导航到首页
      navigate({ to: "/" })
    },
    onError: (error: any) => {
      console.error("Login failed:", error)
      setError("登录失败，请检查用户名和密码")
    },
  })

  // 登出函数
  const logout = async () => {
    try {
      await authAPI.logout()

      // 清除本地存储
      localStorage.removeItem("access_token")
      localStorage.removeItem("token_type")

      // 清除查询缓存
      queryClient.clear()

      // 导航到登录页
      navigate({ to: "/login" })
    } catch (error) {
      console.error("Logout failed:", error)
    }
  }

  // 重置错误状态
  const resetError = () => {
    setError(null)
  }

  return {
    user,
    error,
    loginMutation,
    logout,
    resetError,
    isLoading: loginMutation.isPending,
  }
}
