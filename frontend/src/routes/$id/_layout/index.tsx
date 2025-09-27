import { createFileRoute, redirect, useParams } from "@tanstack/react-router"
import { Box, Flex, Text, IconButton, Image, Spinner } from "@chakra-ui/react"
import { useState } from "react"

import ChatInput from "../../../components/chat/ChatInput"
import ChatList from "../../../components/chat/ChatList"
import SideDrawer from "../../../components/Common/SideDrawer"
import { useConversationChat } from "@/hooks/useConversationChat"

export const Route = createFileRoute("/$id/_layout/")({
  component: RouteComponent,
  beforeLoad: async () => {
    const isAuthenticated = localStorage.getItem("access_token")
    if (!isAuthenticated) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function RouteComponent() {
  const params = useParams({ from: "/$id/_layout/" })
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  // 使用聚合钩子，统一管理会话、消息、任务轮询与发送/语音处理
  const {
    character,
    messages,
    loading,
    message,
    setMessage,
    sendText,
    processVoiceFile,
  } = useConversationChat(params.id)

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
            src={character?.avatar_url}
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
            backgroundImage={`url('${character?.avatar_url}')`}
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
              {loading ? (
                <Box
                  flex="1"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Spinner color="white" />
                </Box>
              ) : (
                <ChatList
                  messages={messages}
                  character={{
                    name: character?.name,
                    short_bio: character?.short_bio,
                    persona_text: character?.persona_text,
                  }}
                />
              )}

              {/* 输入区域 - 固定在底部 */}
              <Box flexShrink="0">
                <ChatInput
                  value={message}
                  onChange={setMessage}
                  onSend={sendText}
                  onVoiceClick={async () => {
                    // 简单实现：录音由浏览器外部完成后，选择文件上传并触发语音任务
                    const input = document.createElement("input")
                    input.type = "file"
                    input.accept = "audio/*"
                    input.onchange = async () => {
                      const file = input.files?.[0]
                      if (!file) return
                      await processVoiceFile(file)
                    }
                    input.click()
                  }}
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
