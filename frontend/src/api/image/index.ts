import { request } from "@/utils/request"

export const imageApi = {
  /** 使用AI生成图片，返回已上传的URL */
  generate: async (args: {
    prompt: string
    size?: string
    style?: string
    quality?: string
  }) => {
    const { prompt, size = "832*1088", style = "realistic", quality = "standard" } = args
    return request.post<{ key: string; url: string }>(
      "/v1/image/generate",
      undefined,
      { params: { prompt, size, style, quality } as Record<string, unknown> }
    )
  },
  upload: async (file: File) => {
    const form = new FormData()
    form.append("file", file)
    return request.post<{ url: string; key?: string }>("/v1/image/upload", form)
  },
}


