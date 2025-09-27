import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import { userApi } from "@/api/user"
import { LoginCredentials } from "@/api/user/type"
import { toaster } from "@/components/ui/toaster"

export const useLogin = () => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { isPending: isLoginPending, mutateAsync: login } = useMutation({
    mutationFn: (body: LoginCredentials) => {
      return userApi.login(body)
    },
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("token_type", data.token_type)

      toaster.success({
        title: "欢迎回来",
      })

      // 刷新当前用户信息并跳转首页
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: "/" })
    },
    onError: (error) => {
      toaster.error({
        title: "登录失败",
        description: error.message,
      })
    },
  })

  return {
    isLoginPending,
    login,
  }
}
