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


