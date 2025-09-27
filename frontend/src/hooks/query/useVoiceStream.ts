import { useEffect, useRef, useState } from "react"
import { useUploadAudio } from "@/hooks/query/useUploadAudio"
import { useProcessVoiceMessage } from "@/hooks/query/useProcessVoiceMessage"
import { useTask } from "@/hooks/query/useTask"

/**
 * 电话页音频分片流式处理钩子
 * - 使用 React Query mutation/query 管理请求与任务状态
 * - 内部维护处理队列与音频播放
 */
export const useVoiceStream = (conversationId: string | undefined) => {
  // 播放状态
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioQueueRef = useRef<string[]>([])
  const playingRef = useRef(false)

  // 待处理分片 URL 队列
  const pendingUrlsRef = useRef<string[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [queueBump, setQueueBump] = useState(0) // 触发处理器的依赖

  // 当前任务轮询（React Query）
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null)
  const taskQuery = useTask(currentTaskId, { refetchIntervalMs: 600 })

  const uploadAudioMutation = useUploadAudio()
  const processVoiceMutation = useProcessVoiceMessage()

  const playNext = () => {
    if (!audioRef.current) audioRef.current = new Audio()
    const audio = audioRef.current
    const next = audioQueueRef.current.shift()
    if (!next) {
      playingRef.current = false
      setIsPlaying(false)
      return
    }
    playingRef.current = true
    setIsPlaying(true)
    audio.src = next
    audio.onended = () => {
      playingRef.current = false
      setIsPlaying(false)
      playNext()
    }
    audio.play().catch(() => {
      playingRef.current = false
      setIsPlaying(false)
    })
  }

  const enqueueAudio = (url: string) => {
    audioQueueRef.current.push(url)
    if (!playingRef.current) playNext()
  }

  // 当有待处理分片且当前未处理时，拉起处理器：下发任务 -> 等待完成 -> 入播放队列
  useEffect(() => {
    if (isProcessing) return
    if (!conversationId) return
    if (pendingUrlsRef.current.length === 0) return
    let cancelled = false

    const run = async () => {
      setIsProcessing(true)
      try {
        const url = pendingUrlsRef.current[0]
        const task = await processVoiceMutation.mutateAsync({
          conversation_id: conversationId,
          audio_file_url: url,
        })
        setCurrentTaskId(task.task_id)
      } catch {
        // 丢弃该分片并继续
        pendingUrlsRef.current.shift()
        setIsProcessing(false)
        if (!cancelled) setQueueBump((v) => v + 1)
      }
    }
    run()

    return () => {
      cancelled = true
    }
  }, [conversationId, isProcessing, queueBump, processVoiceMutation])

  // 监听任务完成，完成后取音频并继续下一个
  useEffect(() => {
    const t = taskQuery.data
    if (!currentTaskId || !t) return
    if (t.status === "COMPLETED") {
      const a = t.result?.audio_url as string | undefined
      if (a) enqueueAudio(a)
      // 出队并继续
      pendingUrlsRef.current.shift()
      setCurrentTaskId(null)
      setIsProcessing(false)
      setQueueBump((v) => v + 1)
    } else if (t.status !== "PENDING" && t.status !== "PROCESSING") {
      // 终态但非成功：丢弃并继续
      pendingUrlsRef.current.shift()
      setCurrentTaskId(null)
      setIsProcessing(false)
      setQueueBump((v) => v + 1)
    }
  }, [taskQuery.data, currentTaskId])

  /**
   * 提交一个录音分片（Blob）。内部会：上传 -> 入待处理队列 -> 自动触发处理
   */
  const submitBlob = async (blob: Blob) => {
    if (!blob || blob.size < 8000) return // 过小片段忽略
    // 播放期间或已有任务处理中不再接受新的用户分片，避免重复请求与打断
    if (playingRef.current || isProcessing) return
    try {
      const file = new File([blob], `chunk_${Date.now()}.webm`, {
        type: blob.type || "audio/webm",
      })
      const up = await uploadAudioMutation.mutateAsync(file)
      // 限流：队列过长且正在处理时丢弃该分片
      if (pendingUrlsRef.current.length >= 3 && isProcessing) return
      pendingUrlsRef.current.push(up.audio_url)
      setQueueBump((v) => v + 1)
    } catch {
      // 忽略错误以保持通话流畅
    }
  }

  /**
   * 立即停止播放并清空所有队列/状态
   * - 用于挂断时确保不再继续播放或轮询
   */
  const teardown = () => {
    try {
      if (audioRef.current) {
        // 暂停当前播放并清空音源
        audioRef.current.pause()
        audioRef.current.src = ""
      }
    } catch {}
    // 清空播放队列
    audioQueueRef.current.length = 0
    playingRef.current = false
    setIsPlaying(false)
    // 清空待处理分片与任务
    pendingUrlsRef.current.length = 0
    setCurrentTaskId(null)
    setIsProcessing(false)
  }

  return {
    // 播放
    isPlaying,

    // 队列/任务状态
    isProcessing,

    // 动作
    submitBlob,
    teardown,
  }
}
