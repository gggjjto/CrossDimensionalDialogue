import { useRef, useEffect } from "react"
import { Box, VStack, HStack, Text, Heading } from "@chakra-ui/react"
import ExpandableText from "@/components/Common/ExpandableText"

type Message = {
  id: number
  sender: "user" | "character"
  content: string
}

type ChatListProps = {
  messages: Message[]
}

export default function ChatList({ messages }: ChatListProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop =
        scrollContainerRef.current.scrollHeight
    }
  }

  // 当消息列表更新时，滚动到底部
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <Box
      ref={scrollContainerRef}
      flex="1"
      overflowY="auto"
      p="4"
      pb={6}
      css={{
        "&::-webkit-scrollbar": {
          display: "none",
        },
        "-ms-overflow-style": "none",
        "scrollbar-width": "none",
      }}
    >
      <VStack gap="4" align="stretch">
        {/* 角色简介面板 */}
        <Box
          bg="rgba(0,0,0,0.4)"
          backdropFilter="blur(10px)"
          borderRadius="lg"
          p="6"
          border="1px solid rgba(255,255,255,0.1)"
        >
          <VStack align="start" gap="4">
            <Heading size="md" color="white">
              角色简介
            </Heading>

            <VStack align="start" gap="2" w="full">
              <HStack>
                <Text fontWeight="bold" color="accent.foreground">
                  姓名:
                </Text>
                <Text>金</Text>
              </HStack>

              <HStack align="start">
                <Text fontWeight="bold" color="accent.foreground">
                  身份:
                </Text>
                <Text>
                  户外赛事策划, 爱骑行、攀岩, 擅长把复杂问题拆成简单步骤, 总在
                  "折腾新鲜事"。
                </Text>
              </HStack>
            </VStack>

            {/* 使用Blockquote样式的描述文本 */}
            <Box
              position="relative"
              pl="4"
              borderLeft="3px solid rgba(255,255,255,0.3)"
              w="full"
            >
              <ExpandableText
                maxLines={1}
                fontSize="sm"
                lineHeight="1.6"
                color="rgba(255,255,255,0.9)"
                buttonColor="accent.foreground"
                buttonSize="sm"
              >
                你在圣多利亚大学的军训期间与她认识, 昨天,
                你答应了金去看她的攀岩比赛。
                她是一个充满活力的女孩，总是带着阳光般的笑容，喜欢挑战各种户外运动。
                她的性格开朗，善于与人交流，总能给人带来正能量。
                在攀岩场上，她展现出的毅力和专注力让人印象深刻。
                无论是面对陡峭的岩壁还是生活中的困难，她都能保持乐观积极的态度。
              </ExpandableText>
            </Box>
          </VStack>
        </Box>

        {/* 聊天消息 */}
        {messages.map((msg) => (
          <Box
            key={msg.id}
            alignSelf={msg.sender === "user" ? "flex-end" : "flex-start"}
            maxW="80%"
          >
            <Box
              bg={
                msg.sender === "user"
                  ? "accent.default"
                  : "rgba(255,255,255,0.1)"
              }
              color={msg.sender === "user" ? "accent.foreground" : "white"}
              p="3"
              borderRadius="lg"
              backdropFilter="blur(10px)"
            >
              <Text fontSize="sm">{msg.content}</Text>
            </Box>
          </Box>
        ))}
      </VStack>
    </Box>
  )
}
