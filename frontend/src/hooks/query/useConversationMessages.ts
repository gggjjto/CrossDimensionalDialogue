import { useQuery } from "@tanstack/react-query"
import { conversationsApi } from "@/api/conversations"

/**
 * 使用 React Query 获取会话消息列表
 * - 默认分页：skip=0, limit=50
 */
export const useConversationMessages = (
  conversationId: string | undefined,
  params: { skip?: number; limit?: number } = {}
) => {
  const { skip = 0, limit = 50 } = params

  return useQuery({
    queryKey: ["conversationMessages", conversationId, { skip, limit }],
    enabled: Boolean(conversationId),
    queryFn: async () => {
      if (!conversationId) throw new Error("conversationId is required")
      return conversationsApi.getMessages(conversationId, { skip, limit })
    },
    staleTime: 10_000,
  })
}
