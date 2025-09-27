import { request } from "@/utils/request"

export const voiceApi = {
  uploadAudio: async (file: File) => {
    const form = new FormData()
    form.append("file", file)
    return request.post<{
      success: boolean
      audio_url: string
      filename: string
      file_size: number
    }>("/v1/voice/upload-audio", form, {
      headers: {
        // 让浏览器自动设置 multipart 边界
        // 不手动设置 Content-Type
      },
    })
  },
  processVoiceMessage: async (body: {
    conversation_id: string
    audio_file_url: string
    voice_preference?: string
  }) => {
    return request.post<{
      task_id: string
      status: string
      progress: number
      created_at: string
    }>("/v1/voice/message", body)
  },
}


