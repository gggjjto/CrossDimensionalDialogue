import { useMutation } from "@tanstack/react-query"
import { voiceApi } from "@/api/voice"

/**
 * 提交语音消息处理任务
 * - 返回任务 id 等信息
 */
export const useProcessVoiceMessage = () => {
  return useMutation({
    mutationFn: async (body: {
      conversation_id: string
      audio_file_url: string
      voice_preference?: string
    }) => {
      return voiceApi.processVoiceMessage(body)
    },
  })
}
