import { useQuery } from "@tanstack/react-query"
import { conversationsApi } from "@/api/conversations"

/**
 * 使用 React Query 获取会话详情
 * - 根据 `conversationId` 请求 `/v1/conversations/{id}`
 */
export const useConversation = (conversationId: string | undefined) => {
  return useQuery({
    queryKey: ["conversation", conversationId],
    // 安全保护：如果没有 id，不发起请求
    enabled: Boolean(conversationId),
    queryFn: async () => {
      if (!conversationId) throw new Error("conversationId is required")
      return conversationsApi.getConversation(conversationId)
    },
  })
}
