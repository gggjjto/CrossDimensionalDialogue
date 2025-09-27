import { request } from "@/utils/request"

export const orchestrationApi = {
  /** 发送消息并触发AI回复（异步任务） */
  sendMessage: async (
    conversationId: string,
    body: { message: string; settings?: Record<string, unknown> }
  ) => {
    return request.post<{ task_id: string; status: string; progress: number; created_at: string }>(
      `/v1/orchestration/conversations/${conversationId}/send-message`,
      {
        message: body.message,
        settings: body.settings,
      }
    )
  },
}


