import { useMutation } from "@tanstack/react-query"
import { voiceApi } from "@/api/voice"

/**
 * 上传音频文件，返回上传后的音频地址
 */
export const useUploadAudio = () => {
  return useMutation({
    mutationFn: async (file: File) => {
      return voiceApi.uploadAudio(file)
    },
  })
}
