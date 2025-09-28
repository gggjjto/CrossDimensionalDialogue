import { useEffect, useMemo, useState } from "react"
import { useConversation } from "@/hooks/query/useConversation"
import { useConversationMessages } from "@/hooks/query/useConversationMessages"
import { useSendMessage } from "@/hooks/query/useSendMessage"
import { useTask } from "@/hooks/query/useTask"
import { useUploadAudio } from "@/hooks/query/useUploadAudio"
import { useProcessVoiceMessage } from "@/hooks/query/useProcessVoiceMessage"

/**
 * useConversationChat
 * - 聚合封装会话详情、消息列表、发送文本、上传语音、任务轮询与“流式”渲染
 * - 将复杂的状态管理尽量放入钩子，页面仅消费结果与动作
 */
export const useConversationChat = (conversationId: string | undefined) => {
  // 输入框内容（UI可直接使用）
  const [message, setMessage] = useState("")

  // 聊天消息列表（包含本地乐观项与服务端数据映射）
  const [messages, setMessages] = useState<
    {
      id: number
      sender: "user" | "character"
      content: string
      audioUrl?: string
    }[]
  >([])

  // 角色信息（展示在 UI 左侧与顶部）
  const [character, setCharacter] = useState<{
    name?: string
    short_bio?: string
    avatar_url?: string
    persona_text?: string
  } | null>(null)

  // 标记首次从服务端初始化本地消息是否完成，避免重复覆盖本地状态
  const [initialized, setInitialized] = useState(false)

  // 避免重复处理同一个任务的“流式”渲染
  const [processedTaskIds, setProcessedTaskIds] = useState<
    Record<string, boolean>
  >({})

  // 基础查询：会话与消息
  const conversationQuery = useConversation(conversationId)
  const messagesQuery = useConversationMessages(conversationId, {
    skip: 0,
    limit: 50,
  })
  const loading = conversationQuery.isLoading || messagesQuery.isLoading

  // 会话 -> 角色信息
  useEffect(() => {
    const conv = conversationQuery.data
    if (!conv) return
    setCharacter({
      name: conv.character?.name,
      short_bio:
        (conv.character as any)?.short_bio ?? (conv.character as any)?.shortbio,
      avatar_url: conv.character?.avatar_url,
      persona_text: (conv.character as any)?.persona_text,
    })
  }, [conversationQuery.data])

  // 首次将消息查询结果映射为本地结构
  const initialMappedMessages = useMemo((): {
    id: number
    sender: "user" | "character"
    content: string
    audioUrl?: string
  }[] => {
    const list = messagesQuery.data?.messages || []
    const sorted = [...list].sort(
      (a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
    return sorted.map((m, idx) => ({
      id: idx + 1,
      sender:
        m.sender_type === "user" ? ("user" as const) : ("character" as const),
      content: m.content,
      audioUrl: (m as any).audio_url as string | undefined,
    }))
  }, [messagesQuery.data])

  useEffect(() => {
    if (!initialized && initialMappedMessages.length > 0) {
      setMessages(initialMappedMessages)
      setInitialized(true)
    }
  }, [initialized, initialMappedMessages])

  // 文本发送 & 任务追踪
  const sendMessageMutation = useSendMessage(conversationId)
  const [textTaskId, setTextTaskId] = useState<string | null>(null)
  const textTaskQuery = useTask(textTaskId, { refetchIntervalMs: 800 })

  // 语音上传处理 & 任务追踪
  const uploadAudioMutation = useUploadAudio()
  const processVoiceMutation = useProcessVoiceMessage()
  const [voiceTaskId, setVoiceTaskId] = useState<string | null>(null)
  const voiceTaskQuery = useTask(voiceTaskId, { refetchIntervalMs: 800 })

  // 占位消息：记录当前“思考中...”的 AI 气泡 id（文本/语音分别一个）
  const [currentTextPendingId, setCurrentTextPendingId] = useState<
    number | null
  >(null)
  const [currentVoicePendingId, setCurrentVoicePendingId] = useState<
    number | null
  >(null)

  // 文本任务完成后，执行“流式”渲染
  useEffect(() => {
    const task = textTaskQuery.data
    if (!task || task.status !== "COMPLETED" || !textTaskId) return
    if (processedTaskIds[textTaskId]) return

    const run = async () => {
      const full = task.result?.character_response || ""
      if (!full) return
      // 使用占位消息 id（若存在），否则新建一个
      const baseId = currentTextPendingId ?? Date.now() + 1
      if (!currentTextPendingId) {
        setMessages((prev) => [
          ...prev,
          {
            id: baseId,
            sender: "character",
            content: "",
            audioUrl: task.result?.audio_url as string | undefined,
          },
        ])
      }
      let acc = ""
      const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))
      for (const ch of full) {
        acc += ch
        setMessages((prev) =>
          prev.map((m) =>
            m.id === baseId
              ? {
                  ...m,
                  content: acc,
                  audioUrl: task.result?.audio_url as string | undefined,
                }
              : m
          )
        )
        await delay(20)
      }
      setProcessedTaskIds((prev) => ({ ...prev, [textTaskId]: true }))
      setCurrentTextPendingId(null)
    }
    run()
  }, [textTaskId, textTaskQuery.data, processedTaskIds, currentTextPendingId])

  // 语音任务完成后，执行“流式”渲染
  useEffect(() => {
    const task = voiceTaskQuery.data
    if (!task || task.status !== "COMPLETED" || !voiceTaskId) return
    if (processedTaskIds[voiceTaskId]) return

    const run = async () => {
      const full = task.result?.character_response || ""
      if (!full) return
      const baseId = currentVoicePendingId ?? Date.now() + 1
      if (!currentVoicePendingId) {
        setMessages((prev) => [
          ...prev,
          {
            id: baseId,
            sender: "character",
            content: "",
            audioUrl: task.result?.audio_url as string | undefined,
          },
        ])
      }
      let acc = ""
      const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))
      for (const ch of full) {
        acc += ch
        setMessages((prev) =>
          prev.map((m) =>
            m.id === baseId
              ? {
                  ...m,
                  content: acc,
                  audioUrl: task.result?.audio_url as string | undefined,
                }
              : m
          )
        )
        await delay(20)
      }
      setProcessedTaskIds((prev) => ({ ...prev, [voiceTaskId]: true }))
      setCurrentVoicePendingId(null)
    }
    run()
  }, [
    voiceTaskId,
    voiceTaskQuery.data,
    processedTaskIds,
    currentVoicePendingId,
  ])

  /**
   * 发送当前输入框文本（内置乐观更新）
   */
  const sendText = async () => {
    const text = message.trim()
    if (!text) return
    const optimistic = {
      id: Date.now(),
      sender: "user" as const,
      content: text,
    }
    setMessages((prev) => [...prev, optimistic])
    // 插入 AI 占位气泡
    const pendingId = Date.now() + 1
    setMessages((prev) => [
      ...prev,
      { id: pendingId, sender: "character", content: "思考中..." },
    ])
    setCurrentTextPendingId(pendingId)
    setMessage("")
    try {
      const res = await sendMessageMutation.mutateAsync({ message: text })
      setTextTaskId(res.task_id)
    } catch {
      // 失败回滚乐观项
      setMessages((prev) =>
        prev.filter((m) => m.id !== optimistic.id && m.id !== pendingId)
      )
      setMessage(text)
      setCurrentTextPendingId(null)
    }
  }

  /**
   * 处理外部选择的音频文件（上传 -> 下发任务）
   */
  const processVoiceFile = async (file: File) => {
    if (!file || !conversationId) return
    // 插入 AI 占位气泡
    const pendingId = Date.now() + 1
    setMessages((prev) => [
      ...prev,
      { id: pendingId, sender: "character", content: "思考中..." },
    ])
    setCurrentVoicePendingId(pendingId)
    try {
      const up = await uploadAudioMutation.mutateAsync(file)
      const task = await processVoiceMutation.mutateAsync({
        conversation_id: conversationId,
        audio_file_url: up.audio_url,
      })
      setVoiceTaskId(task.task_id)
    } catch {
      // 失败则移除占位气泡
      setMessages((prev) => prev.filter((m) => m.id !== pendingId))
      setCurrentVoicePendingId(null)
    }
  }

  return {
    // 显示数据
    character,
    messages,
    loading,

    // 输入框状态
    message,
    setMessage,

    // 动作
    sendText,
    processVoiceFile,
  }
}
