import { useMutation } from "@tanstack/react-query"

import { userApi } from "@/api/user"
import { LoginCredentials } from "@/api/user/type"
import { toaster } from "@/components/ui/toaster"

export const useLogin = () => {
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
