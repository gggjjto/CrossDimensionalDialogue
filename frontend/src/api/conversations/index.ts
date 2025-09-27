import { request } from "@/utils/request"
import type {
  CharacterGenerateRequest,
  CharacterGenerateResponse,
} from "./type"

export const conversationsApi = {
  /** AI 生成角色设定 */
  generateCharacter: async (body: CharacterGenerateRequest) => {
    return request.post<CharacterGenerateResponse>("/v1/conversations/generate", body)
  },
}


