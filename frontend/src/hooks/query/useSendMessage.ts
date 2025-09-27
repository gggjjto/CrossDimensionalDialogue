import { useMutation } from "@tanstack/react-query"
import { orchestrationApi } from "@/api/orchestration"

/**
 * 发送文本消息，触发编排任务
 * - 返回 { task_id, status, progress, created_at }
 */
export const useSendMessage = (conversationId: string | undefined) => {
  return useMutation({
    mutationFn: async (body: {
      message: string
      settings?: Record<string, unknown>
    }) => {
      if (!conversationId) throw new Error("conversationId is required")
      return orchestrationApi.sendMessage(conversationId, body)
    },
  })
}
