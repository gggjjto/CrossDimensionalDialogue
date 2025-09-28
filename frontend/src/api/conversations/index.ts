import { request } from "@/utils/request"
import type {
  CharacterGenerateRequest,
  CharacterGenerateResponse,
  ConversationCreateRequest,
  ConversationPublic,
  ConversationWithDetails,
  MessageListResponse,
  MessagePublic,
  SendMessageRequest,
  ConversationsListResponse,
  ConversationLookupResponse,
} from "./type"

export const conversationsApi = {
  /** AI 生成角色设定 */
  generateCharacter: async (body: CharacterGenerateRequest) => {
    return request.post<CharacterGenerateResponse>("/v1/conversations/generate", body)
  },
  /** 创建会话 */
  createConversation: async (body: ConversationCreateRequest) => {
    return request.post<ConversationPublic>("/v1/conversations/", body)
  },
  /** 获取会话列表（最近聊天） */
  getConversations: async (params: {
    skip?: number
    limit?: number
    order_by?: "last_message_at" | "created_at" | "updated_at" | "title"
    order?: "asc" | "desc"
  } = {}) => {
    return request.get<ConversationsListResponse>("/v1/conversations/", {
      params: {
        skip: params.skip ?? 0,
        limit: params.limit ?? 10,
        order_by: params.order_by ?? "last_message_at",
        order: params.order ?? "desc",
      } as Record<string, unknown>,
    })
  },
  /** 会话详情 */
  getConversation: async (id: string) => {
    return request.get<ConversationWithDetails>(`/v1/conversations/${id}`)
  },
  /** 通过角色ID查找已存在的会话 */
  lookupByCharacter: async (characterId: string) => {
    return request.get<ConversationLookupResponse>(
      `/v1/conversations/lookup/by-character/${characterId}`
    )
  },
  /** 消息列表 */
  getMessages: async (
    conversationId: string,
    params: { skip?: number; limit?: number } = {}
  ) => {
    return request.get<MessageListResponse>(
      `/v1/conversations/${conversationId}/messages`,
      { params }
    )
  },
  /** 创建消息 */
  createMessage: async (conversationId: string, body: SendMessageRequest) => {
    return request.post<MessagePublic>(
      `/v1/conversations/${conversationId}/messages`,
      {
        sender_type: body.sender_type,
        content: body.content,
        content_type: body.content_type ?? "text",
      }
    )
  },
}


