import { useQuery } from "@tanstack/react-query"
import { request } from "@/utils/request"
import { CurrentUser } from "@/api/user/type"
import { isLoggedIn } from "@/hooks/query/useAuth"



export const useUserInfo = () => {
    const { data: user } = useQuery({
        queryKey: ["currentUser"],
        queryFn: async (): Promise<CurrentUser> => {
          const data = await request.get<CurrentUser>("/v1/users/me")
          return data
        },
        enabled: isLoggedIn(),
    })
    return user
}