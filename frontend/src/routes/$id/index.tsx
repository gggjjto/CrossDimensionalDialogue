import { createFileRoute } from "@tanstack/react-router"
import { Box, Flex, Text, IconButton, Image } from "@chakra-ui/react"
import { useState } from "react"
import ChatInput from "../../components/chat/ChatInput"
import ChatList from "../../components/chat/ChatList"
import SideDrawer from "../../components/Common/SideDrawer"

export const Route = createFileRoute("/$id/")({
  component: RouteComponent,
})

function RouteComponent() {
  const [message, setMessage] = useState("")
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "character" as const,
      content:
        "你好呀!我是小樱,很高兴见到你(开心地眨眨眼,脸上露出甜甜的笑容)今天想聊些什么呢?我可以陪你聊天哦~",
    },
    {
      id: 2,
      sender: "user" as const,
      content: "你好~",
    },
  ])

  // 发送消息
  const handleSendMessage = () => {
    if (message.trim()) {
      setMessages([
        ...messages,
        { id: Date.now(), sender: "user" as const, content: message },
      ])
      setMessage("")
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
          onClick={() => setIsDrawerOpen(true)}
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
            {/* 聊天界面 */}
            <Box flex="1" display="flex" flexDirection="column" minH="0">
              {/* 聊天内容 - 可滚动区域（包含简介和消息） */}
              <ChatList messages={messages} />

              {/* 输入区域 - 固定在底部 */}
              <Box flexShrink="0">
                <ChatInput
                  value={message}
                  onChange={setMessage}
                  onSend={handleSendMessage}
                  onVoiceClick={() => {}}
                  minHeightPx={40}
                  maxHeightPx={200}
                />
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

      {/* 侧边抽屉 */}
      <SideDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </Box>
  )
}
