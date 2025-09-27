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
  /** 搜索公开角色（服务端搜索） */
  search: async (
    query: string,
    params: { offset?: number; limit?: number; search_type?: "text" | "vector" | "hybrid"; is_active?: boolean; tag_ids?: string[] } = {}
  ) => {
    return request.get<{ results: any[]; total: number; query: string; search_type: string }>(
      "/v1/characters/search",
      {
        params: {
          query,
          search_type: params.search_type ?? "text",
          offset: params.offset ?? 0,
          limit: params.limit ?? 20,
          is_active: params.is_active ?? true,
          tag_ids: params.tag_ids,
        } as Record<string, unknown>,
      }
    )
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


