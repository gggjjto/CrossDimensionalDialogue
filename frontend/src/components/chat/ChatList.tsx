import { useRef, useEffect, useState } from "react"
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  IconButton,
} from "@chakra-ui/react"
import { LuVolume2, LuVolumeX } from "react-icons/lu"
import ExpandableText from "@/components/Common/ExpandableText"

type Message = {
  id: number
  sender: "user" | "character"
  content: string
  audioUrl?: string
}

type ChatListProps = {
  messages: Message[]
  character?: { name?: string; short_bio?: string; persona_text?: string }
}

export default function ChatList({ messages, character }: ChatListProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [playingId, setPlayingId] = useState<number | null>(null)

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

  const togglePlay = async (msg: Message) => {
    if (!msg.audioUrl) return
    if (!audioRef.current) {
      audioRef.current = new Audio()
      audioRef.current.addEventListener("ended", () => setPlayingId(null))
    }
    const audio = audioRef.current
    // 切换同一条消息 => 暂停
    if (playingId === msg.id) {
      audio.pause()
      setPlayingId(null)
      return
    }
    try {
      audio.pause()
      audio.src = msg.audioUrl
      await audio.play()
      setPlayingId(msg.id)
    } catch {
      // 忽略播放失败
    }
  }

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
            <Heading size="md" color="白色">
              角色简介
            </Heading>

            <VStack align="start" gap="2" w="full">
              <HStack>
                <Text fontWeight="bold" color="accent.foreground">
                  姓名:
                </Text>
                <Text>{character?.name || "-"}</Text>
              </HStack>

              <HStack align="start">
                {/* <Text fontWeight="bold" color="accent.foreground">
                  简介:
                </Text> */}
                <Text>简介: {character?.short_bio || "-"}</Text>
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
                {character?.persona_text ||
                  character?.short_bio ||
                  "暂无更多描述"}
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
              {msg.audioUrl && (
                <HStack mt="2" gap="2">
                  <IconButton
                    aria-label="播放语音"
                    size="xs"
                    variant="ghost"
                    color="accent.foreground"
                    onClick={() => togglePlay(msg)}
                  >
                    {playingId === msg.id ? <LuVolumeX /> : <LuVolume2 />}
                  </IconButton>
                  <Text fontSize="xs" color="rgba(255,255,255,0.8)">
                    {playingId === msg.id ? "正在播放" : "播放语音"}
                  </Text>
                </HStack>
              )}
            </Box>
          </Box>
        ))}
      </VStack>
    </Box>
  )
}
