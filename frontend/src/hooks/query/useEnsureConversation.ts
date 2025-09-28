import { useMutation } from "@tanstack/react-query"
import { conversationsApi } from "@/api/conversations"
import { charactersApi } from "@/api/characters"

export const useEnsureConversation = () => {
  const ensureMutation = useMutation({
    mutationFn: async (params: { characterId: string; title?: string }) => {
      const { characterId, title } = params
      try {
        const res = await conversationsApi.lookupByCharacter(characterId)
        const exists = res?.exists
        const convId = res?.conversation_id
        if (exists && convId) return convId
      } catch {}

      // 不存在或查询失败时，创建新会话，并从 example_lines 选一句作为开场白
      const created = await conversationsApi.createConversation({
        title: title ?? "",
        character_id: characterId,
      })

      try {
        // 获取角色详情（从公开列表中匹配当前角色）
        const list = await charactersApi.getPublicCharacters({ skip: 0, limit: 100, is_active: true })
        const picked = (list.characters || []).find((c) => c.id === characterId) as any
        const lines: string[] | undefined = picked?.example_lines
        if (Array.isArray(lines) && lines.length > 0) {
          const idx = Math.floor(Math.random() * lines.length)
          const content = lines[idx]
          if (content && content.trim()) {
            await conversationsApi.createMessage(String(created.id), {
              sender_type: "character",
              content,
            })
          }
        }
      } catch {}

      return created.id
    },
  })

  return {
    ensureConversation: ensureMutation.mutateAsync,
    isEnsuring: ensureMutation.isPending,
  }
}


