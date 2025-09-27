import { Box, Flex, Stack, Text } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { userApi } from "@/api/user"

export default function UserStats() {
  const [stats, setStats] = useState<{
    character_count: number
    conversation_count: number
    created_at?: string
  }>({ character_count: 0, conversation_count: 0, created_at: undefined })

  useEffect(() => {
    ;(async () => {
      try {
        const me = await userApi.me()
        setStats({
          character_count: me.character_count ?? 0,
          conversation_count: me.conversation_count ?? 0,
          created_at: me.created_at,
        })
      } catch {
        // ignore
      }
    })()
  }, [])

  return (
    <Box>
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        使用统计
      </Text>
      <Stack gap={3}>
        <Flex justify="space-between" align="center">
          <Text color="fg.muted">创建的智能体</Text>
          <Text fontWeight="medium">{stats.character_count}</Text>
        </Flex>
        <Flex justify="space-between" align="center">
          <Text color="fg.muted">对话次数</Text>
          <Text fontWeight="medium">{stats.conversation_count}</Text>
        </Flex>
        <Flex justify="space-between" align="center">
          <Text color="fg.muted">注册时间</Text>
          <Text fontWeight="medium">
            {stats.created_at ? new Date(stats.created_at).toLocaleDateString() : "-"}
          </Text>
        </Flex>
      </Stack>
    </Box>
  )
}
