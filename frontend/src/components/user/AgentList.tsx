import { Box, Flex, Text } from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"

import AgentCard from "./AgentCard"

interface Agent {
  id: string
  title: string
  slogan: string
  tags?: string[]
  imageSrc: string
}

interface AgentListProps {
  agents: Agent[]
  showCreateLink?: boolean
}

export default function AgentList({ agents, showCreateLink = true }: AgentListProps) {
  // 将agents分组，每行两个
  const groupedAgents = []
  for (let i = 0; i < agents.length; i += 2) {
    groupedAgents.push(agents.slice(i, i + 2))
  }

  return (
    <Box px={40} py={4}>
      {/* 智能体卡片列表 - 每行两个 */}
      {groupedAgents.map((row, rowIndex) => (
        <Flex key={rowIndex} gap={6} mb={6}>
          {row.map((agent) => (
            <Box key={agent.id} flex="1">
              <AgentCard
                title={agent.title}
                slogan={agent.slogan}
                tags={agent.tags}
                imageSrc={agent.imageSrc}
              />
            </Box>
          ))}
          {/* 如果这一行只有一个卡片，添加一个空的占位符 */}
          {row.length === 1 && <Box flex="1" />}
        </Flex>
      ))}

      {/* 底部提示和创建链接 */}
      {agents.length > 0 && (
        <Box textAlign="center" mt={8} pt={4}>
          <Text fontSize="sm" color="fg.muted" mb={2}>
            没有更多啦~
          </Text>
          {showCreateLink && (
            <RouterLink
              to="/create-agent"
              style={{
                color: "var(--chakra-colors-info-default)",
                fontSize: "14px",
                fontWeight: "500",
                textDecoration: "none"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.textDecoration = "underline"
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.textDecoration = "none"
              }}
            >
              点击去创建→
            </RouterLink>
          )}
        </Box>
      )}
    </Box>
  )
}
