import { request } from "@/utils/request"
import type {
  GetPublicCharactersParams,
  ReadAllCharactersResponse,
} from "./type"
import type { CharacterPublic } from "./type"

export const charactersApi = {
  /** 获取公开角色列表（无需登录） */
  getPublicCharacters: async (params: GetPublicCharactersParams = {}) => {
    return request.get<ReadAllCharactersResponse>("/v1/characters/public", {
      params: { ...params } as Record<string, unknown>,
    })
  },
  /** 创建角色（需要登录） */
  createCharacter: async (body: {
    name: string
    short_bio: string
    persona_text: string
    example_lines?: string[]
    source?: string
    is_active?: boolean
    is_public?: boolean
  }) => {
    return request.post<CharacterPublic>("/v1/characters/", body)
  },
  /** 为角色生成图片并返回 URL（832x1088） */
  generateCharacterImage: async (characterId: string, style: string) => {
    return request.post<{ character_id: string; avatar_url: string; style: string; size: string }>(
      `/v1/characters/${characterId}/generate-image`,
      undefined,
      {
        params: {
          style: style === "anime" ? "anime" : "realistic",
          size: "832*1088",
        },
      }
    )
  },
}


