export interface CharacterGenerateRequest {
  name: string
  character_type: string
  background?: string
}

export interface CharacterGenerateResponse {
  name: string
  short_bio: string
  persona_text: string
  example_lines: string[]
  suggested_voice: string
}

export interface ConversationCreateRequest {
  title: string
  description?: string
  character_id: string
  settings?: Record<string, unknown>
}

export interface ConversationPublic {
  id: string
  user_id: string
  character_id: string
  title: string
  description?: string
  message_count: number
  last_message_at?: string
  created_at: string
  updated_at: string
}

export interface CharacterSummary {
  id: string
  name: string
  short_bio?: string
  avatar_url?: string
  persona_text?: string
}

export interface ConversationWithDetails extends ConversationPublic {
  character?: CharacterSummary
}

export interface ConversationsListResponse {
  conversations: ConversationWithDetails[]
  total: number
  skip: number
  limit: number
}

export interface MessagePublic {
  id: string
  conversation_id: string
  sender_type: "user" | "character" | "system"
  sender_id?: string
  content: string
  content_type: "text" | "audio" | "image" | "file"
  created_at: string
}

export interface MessageListResponse {
  messages: MessagePublic[]
  total: number
  skip: number
  limit: number
}

export interface SendMessageRequest {
  content: string
  sender_type: "user" | "character" | "system"
  content_type?: "text" | "audio" | "image" | "file"
}


export interface ConversationLookupResponse {
  exists: boolean
  conversation_id?: string
  conversation?: any
}
