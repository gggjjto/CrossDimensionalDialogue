import { createFileRoute } from "@tanstack/react-router"
import {
  Box,
  Flex,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  IconButton,
  Image,
  Heading,
} from "@chakra-ui/react"
import { useState } from "react"
import { FaCaretDown } from "react-icons/fa"

export const Route = createFileRoute("/$id/")({
  component: RouteComponent,
})

function RouteComponent() {
  const [message, setMessage] = useState("")
  const [isExpanded, setIsExpanded] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "character",
      content:
        "你好呀!我是小樱,很高兴见到你(开心地眨眨眼,脸上露出甜甜的笑容)今天想聊些什么呢?我可以陪你聊天哦~",
    },
    {
      id: 2,
      sender: "user",
      content: "你好~",
    },
  ])

  const handleSendMessage = () => {
    if (message.trim()) {
      setMessages([
        ...messages,
        { id: Date.now(), sender: "user", content: message },
      ])
      setMessage("")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <Box minH="100vh" bg="bg.default">
      {/* 汉堡菜单 */}
      <Box position="absolute" top="4" left="4" zIndex="10">
        <IconButton
          aria-label="菜单"
          variant="ghost"
          color="white"
          bg="rgba(0,0,0,0.3)"
          _hover={{ bg: "rgba(0,0,0,0.5)" }}
          borderRadius="md"
        >
          <Box>
            <Box w="20px" h="2px" bg="white" mb="1" />
            <Box w="20px" h="2px" bg="white" mb="1" />
            <Box w="20px" h="2px" bg="white" />
          </Box>
        </IconButton>
      </Box>

      <Flex h="100vh">
        {/* 左侧角色图片区域 */}
        <Box flex="1" position="relative" overflow="hidden">
          <Image
            src="/assets/images/agent.png"
            alt="角色图片"
            w="100%"
            h="100%"
            objectFit="cover"
          />
        </Box>

        {/* 右侧内容区域 */}
        <Box
          flex="1"
          position="relative"
          bg="linear-gradient(135deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6))"
          backdropFilter="blur(10px)"
          color="white"
        >
          {/* 背景图片（模糊） */}
          <Box
            position="absolute"
            top="0"
            left="0"
            right="0"
            bottom="0"
            backgroundImage="url('/assets/images/agent.png')"
            backgroundSize="cover"
            backgroundPosition="center"
            filter="blur(20px)"
            opacity="0.3"
            zIndex="-1"
          />

          <Flex direction="column" h="100%" p="6">
            {/* 角色简介面板 */}
            <Box
              bg="rgba(0,0,0,0.4)"
              backdropFilter="blur(10px)"
              borderRadius="lg"
              p="6"
              mb="6"
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
                      户外赛事策划, 爱骑行、攀岩, 擅长把复杂问题拆成简单步骤,
                      总在 "折腾新鲜事"。
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
                  <Text
                    fontSize="sm"
                    lineHeight="1.6"
                    color="rgba(255,255,255,0.9)"
                  >
                    你在圣多利亚大学的军训期间与她认识, 昨天,
                    你答应了金去看她的攀岩比赛。
                  </Text>

                  <Box
                    maxH={isExpanded ? "200px" : "0"}
                    overflow="hidden"
                    transition="max-height 0.3s ease-in-out, opacity 0.3s ease-in-out"
                    opacity={isExpanded ? 1 : 0}
                  >
                    <Text
                      fontSize="sm"
                      lineHeight="1.6"
                      color="rgba(255,255,255,0.9)"
                      mt="2"
                    >
                      她是一个充满活力的女孩，总是带着阳光般的笑容，喜欢挑战各种户外运动。
                      她的性格开朗，善于与人交流，总能给人带来正能量。
                      在攀岩场上，她展现出的毅力和专注力让人印象深刻。
                      无论是面对陡峭的岩壁还是生活中的困难，她都能保持乐观积极的态度。
                    </Text>
                  </Box>
                </Box>

                {/* 展开/收起按钮 */}
                <HStack>
                  <Button
                    variant="ghost"
                    color="accent.foreground"
                    size="sm"
                    onClick={() => setIsExpanded(!isExpanded)}
                    _hover={{ bg: "rgba(255,255,255,0.1)" }}
                  >
                    {isExpanded ? "收起" : "展开"}
                  </Button>
                  <Box
                    transform={isExpanded ? "rotate(180deg)" : "rotate(0deg)"}
                    transition="transform 0.2s"
                  >
                    <FaCaretDown />
                  </Box>
                </HStack>
              </VStack>
            </Box>

            {/* 聊天界面 */}
            <Box flex="1" display="flex" flexDirection="column">
              <VStack gap="4" flex="1" overflowY="auto" align="stretch">
                {messages.map((msg) => (
                  <Box
                    key={msg.id}
                    alignSelf={
                      msg.sender === "user" ? "flex-end" : "flex-start"
                    }
                    maxW="80%"
                  >
                    <Box
                      bg={
                        msg.sender === "user"
                          ? "accent.default"
                          : "rgba(255,255,255,0.1)"
                      }
                      color={
                        msg.sender === "user" ? "accent.foreground" : "white"
                      }
                      p="3"
                      borderRadius="lg"
                      backdropFilter="blur(10px)"
                    >
                      <Text fontSize="sm">{msg.content}</Text>
                    </Box>
                  </Box>
                ))}
              </VStack>

              {/* 输入区域 */}
              <Box mt="4">
                <HStack gap="2">
                  <IconButton
                    aria-label="语音"
                    variant="ghost"
                    color="accent.foreground"
                    size="sm"
                    _hover={{ bg: "rgba(255,255,255,0.1)" }}
                  >
                    📞
                  </IconButton>

                  <Input
                    placeholder="发送消息"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    bg="rgba(255,255,255,0.1)"
                    border="1px solid rgba(255,255,255,0.2)"
                    color="white"
                    _placeholder={{ color: "rgba(255,255,255,0.6)" }}
                    _focus={{ borderColor: "accent.default" }}
                    flex="1"
                  />

                  <IconButton
                    aria-label="发送"
                    variant="ghost"
                    color="accent.foreground"
                    size="sm"
                    onClick={handleSendMessage}
                    _hover={{ bg: "rgba(255,255,255,0.1)" }}
                  >
                    ✈️
                  </IconButton>
                </HStack>

                <Text
                  fontSize="xs"
                  color="rgba(255,255,255,0.6)"
                  mt="2"
                  textAlign="center"
                >
                  按 Enter 发送消息, Shift + Enter 换行
                </Text>
              </Box>
            </Box>
          </Flex>
        </Box>
      </Flex>
    </Box>
  )
}
