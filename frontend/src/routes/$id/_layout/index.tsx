import { createFileRoute, redirect, useParams } from "@tanstack/react-router"
import { Box, Flex, Text, IconButton, Image, Spinner } from "@chakra-ui/react"
import { useEffect, useState } from "react"

import ChatInput from "../../../components/chat/ChatInput"
import ChatList from "../../../components/chat/ChatList"
import SideDrawer from "../../../components/Common/SideDrawer"
import { conversationsApi } from "@/api/conversations"
import { orchestrationApi } from "@/api/orchestration"
import { tasksApi } from "@/api/tasks"
import { voiceApi } from "@/api/voice"

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
  const [message, setMessage] = useState("")
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [messages, setMessages] = useState<
    {
      id: number
      sender: "user" | "character"
      content: string
      audioUrl?: string
    }[]
  >([])
  const [loading, setLoading] = useState(true)
  const [character, setCharacter] = useState<{
    name?: string
    short_bio?: string
    avatar_url?: string
    persona_text?: string
  } | null>(null)

  // 加载会话详情与消息
  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        setLoading(true)
        const conv = await conversationsApi.getConversation(params.id)
        if (!mounted) return
        setCharacter({
          name: conv.character?.name,
          short_bio:
            (conv.character as any)?.short_bio ??
            (conv.character as any)?.shortbio,
          avatar_url: conv.character?.avatar_url,
          persona_text: (conv.character as any)?.persona_text,
        })
        const msgs = await conversationsApi.getMessages(params.id, {
          skip: 0,
          limit: 50,
        })
        if (!mounted) return
        const mapped: {
          id: number
          sender: "user" | "character"
          content: string
          audioUrl?: string
        }[] = msgs.messages.map((m, idx) => ({
          id: idx + 1,
          sender: m.sender_type === "user" ? "user" : "character",
          content: m.content,
          audioUrl: (m as any).audio_url,
        }))
        setMessages(mapped)
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => {
      mounted = false
    }
  }, [params.id])

  // 发送消息
  const handleSendMessage = async () => {
    const text = message.trim()
    if (!text) return
    // 先本地追加，提升体验
    const optimistic = {
      id: Date.now(),
      sender: "user" as const,
      content: text,
    }
    setMessages([...messages, optimistic])
    setMessage("")
    try {
      // 1) 触发编排：异步任务
      const task = await orchestrationApi.sendMessage(params.id, {
        message: text,
      })
      // 2) 轮询任务，直到 COMPLETED/FAILED
      let tries = 0
      const maxTries = 20
      const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))
      while (tries < maxTries) {
        const t = await tasksApi.getTask(task.task_id)
        if (t.status === "COMPLETED") {
          // 模拟流式：逐步渲染字符
          const full = t.result?.character_response || ""
          if (full) {
            // 先插入一个空的角色消息
            const baseId = Date.now() + 1
            setMessages((prev) => [
              ...prev,
              {
                id: baseId,
                sender: "character",
                content: "",
                audioUrl: t.result?.audio_url as string | undefined,
              },
            ])
            // 逐字追加
            let acc = ""
            for (const ch of full) {
              acc += ch
              setMessages((prev) =>
                prev.map((m) => (m.id === baseId ? { ...m, content: acc } : m))
              )
              await delay(20) // 20ms/字符，营造流式感
            }
          }
          // 若有 TTS 音频，边显示边播放
          if (t.result?.audio_url) {
            // 已在消息上提供点击播放按钮
          }
          break
        }
        if (
          t.status === "FAILED" ||
          t.status === "CANCELLED" ||
          t.status === "TIMEOUT"
        ) {
          break
        }
        tries += 1
        await delay(800)
      }
      // 3) 可选：最终再刷新一次，确保和服务端完全一致
      // const latest = await conversationsApi.getMessages(params.id, { skip: 0, limit: 50 })
      // const mapped: { id: number; sender: "user" | "character"; content: string }[] = latest.messages.map(
      //   (m, idx) => ({
      //     id: idx + 1,
      //     sender: m.sender_type === "user" ? "user" : "character",
      //     content: m.content,
      //   })
      // )
      // setMessages(mapped)
    } catch {
      // 简单回滚：失败时移除刚追加的乐观项
      setMessages((prev) => prev.filter((m) => m.id !== optimistic.id))
      setMessage(text)
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
          {character?.avatar_url ? (
            <Image
              src={character.avatar_url}
              alt="角色图片"
              w="100%"
              h="100%"
              objectFit="cover"
            />
          ) : (
            <Image
              src="/assets/images/agent.png"
              alt="角色图片"
              w="100%"
              h="100%"
              objectFit="cover"
            />
          )}
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
            backgroundImage={
              character?.avatar_url
                ? `url('${character.avatar_url}')`
                : "url('/assets/images/agent.png')"
            }
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
                  onSend={handleSendMessage}
                  onVoiceClick={async () => {
                    // 简单实现：录音由浏览器外部完成后，选择文件上传并触发语音任务
                    const input = document.createElement("input")
                    input.type = "file"
                    input.accept = "audio/*"
                    input.onchange = async () => {
                      const file = input.files?.[0]
                      if (!file) return
                      const up = await voiceApi.uploadAudio(file)
                      const task = await voiceApi.processVoiceMessage({
                        conversation_id: params.id,
                        audio_file_url: up.audio_url,
                      })
                      // 轮询任务并刷新消息
                      let tries = 0
                      const maxTries = 20
                      const delay = (ms: number) =>
                        new Promise((r) => setTimeout(r, ms))
                      while (tries < maxTries) {
                        const t = await tasksApi.getTask(task.task_id)
                        if (t.status === "COMPLETED") {
                          const full =
                            (t.result?.character_response as string) || ""
                          if (full) {
                            const baseId = Date.now() + 1
                            setMessages((prev) => [
                              ...prev,
                              {
                                id: baseId,
                                sender: "character",
                                content: "",
                                audioUrl: t.result?.audio_url as
                                  | string
                                  | undefined,
                              },
                            ])
                            let acc = ""
                            for (const ch of full) {
                              acc += ch
                              setMessages((prev) =>
                                prev.map((m) =>
                                  m.id === baseId ? { ...m, content: acc } : m
                                )
                              )
                              await delay(20)
                            }
                          }
                          // 点击按钮播放语音
                          break
                        }
                        if (
                          t.status === "FAILED" ||
                          t.status === "CANCELLED" ||
                          t.status === "TIMEOUT"
                        ) {
                          break
                        }
                        tries += 1
                        await delay(800)
                      }
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
