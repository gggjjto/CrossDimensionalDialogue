export interface CharacterTagPublic {
  id: string
  name: string
  description?: string
  color?: string
  created_at: string
  updated_at: string
}

export interface CharacterPublic {
  id: string
  name: string
  short_bio: string
  avatar_url?: string
  is_active: boolean
  is_public: boolean
  created_at: string
  updated_at: string
  tags?: CharacterTagPublic[]
}

export interface ReadAllCharactersResponse {
  characters: CharacterPublic[]
  total: number
  skip: number
  limit: number
}

export interface GetPublicCharactersParams {
  skip?: number
  limit?: number
  is_active?: boolean
  tag_ids?: string[]
}


