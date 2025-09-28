import {
  createFileRoute,
  redirect,
  useNavigate,
  useParams,
} from "@tanstack/react-router"
import { Box, Flex, VStack, HStack, Text, Button } from "@chakra-ui/react"
import { FaPhoneSlash, FaMicrophone, FaMicrophoneSlash } from "react-icons/fa"
import { useState, useEffect, useRef } from "react"
import { useConversation } from "@/hooks/query/useConversation"

import { useVoiceStream } from "@/hooks/query/useVoiceStream"

export const Route = createFileRoute("/$id/_layout/phone")({
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
  const [isMuted, setIsMuted] = useState(false)
  const isMutedRef = useRef(false)
  const [isRecording, setIsRecording] = useState(false)
  const isSpaceHeldRef = useRef(false)
  const [audioLevels, setAudioLevels] = useState<number[]>([])
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const rafIdRef = useRef<number | null>(null)

  const navigate = useNavigate()
  const { id } = useParams({ from: "/$id/_layout/phone" })
  // 从语音流钩子中获取控制项与清理方法
  const { isPlaying, submitBlob, teardown } = useVoiceStream(id)
  const conversationQuery = useConversation(id)
  const avatarUrl = conversationQuery.data?.character?.avatar_url || "/assets/images/agent.png"

  // 准备麦克风与可视化（不自动开始录音）
  useEffect(() => {
    let mounted = true

    const start = async () => {
      try {
        // 请求麦克风
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        })
        if (!mounted) return
        mediaStreamRef.current = stream
        // 可视化
        const audioCtx = new (window.AudioContext ||
          (window as any).webkitAudioContext)()
        const source = audioCtx.createMediaStreamSource(stream)
        const analyser = audioCtx.createAnalyser()
        analyser.fftSize = 256
        source.connect(analyser)
        analyserRef.current = analyser
        const dataArray = new Uint8Array(analyser.frequencyBinCount)
        const tick = () => {
          analyser.getByteFrequencyData(dataArray)
          const buckets = 5
          const step = Math.floor(dataArray.length / buckets)
          const levels = new Array(buckets).fill(0).map((_, i) => {
            const slice = dataArray.slice(i * step, (i + 1) * step)
            const avg = slice.reduce((a, b) => a + b, 0) / slice.length / 255
            return Math.max(0.2, Math.min(1, avg))
          })
          setAudioLevels(levels)
          rafIdRef.current = requestAnimationFrame(tick)
        }
        tick()

        // 录音器
        const mimeTypes = [
          "audio/webm;codecs=opus",
          "audio/webm",
          "audio/ogg;codecs=opus",
        ]
        const mimeType =
          mimeTypes.find((t) => MediaRecorder.isTypeSupported(t)) || ""
        const recorder = new MediaRecorder(
          stream,
          mimeType ? { mimeType } : undefined
        )
        recorderRef.current = recorder
        recorder.ondataavailable = async (ev) => {
          const blob = ev.data
          if (!blob || blob.size < 8000) return // 过小片段忽略
          if (isMutedRef.current) return
          await submitBlob(blob)
        }
      } catch {
        // 权限被拒或不支持
      }
    }

    start()
    return () => {
      mounted = false
      // 清理
      if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current)
      const rec = recorderRef.current
      if (rec && rec.state !== "inactive") rec.stop()
      const ms = mediaStreamRef.current
      ms?.getTracks().forEach((t) => t.stop())
      recorderRef.current = null
      mediaStreamRef.current = null
      analyserRef.current = null
    }
  }, [id])

  // 空格键按住开始录音，松开停止并提交
  useEffect(() => {
    const isEditable = (el: Element | null) => {
      if (!el) return false
      const tag = (el as HTMLElement).tagName
      const editable = (el as HTMLElement).isContentEditable
      return (
        editable ||
        tag === "INPUT" ||
        tag === "TEXTAREA" ||
        tag === "SELECT"
      )
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code !== "Space") return
      if (isEditable(document.activeElement)) return
      if (isSpaceHeldRef.current) return
      e.preventDefault()
      // 开始录音
      try {
        const rec = recorderRef.current
        if (rec && rec.state === "inactive") {
          rec.start()
          isSpaceHeldRef.current = true
          setIsRecording(true)
        }
      } catch {}
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code !== "Space") return
      if (!isSpaceHeldRef.current) return
      e.preventDefault()
      // 停止录音
      try {
        const rec = recorderRef.current
        if (rec && rec.state === "recording") {
          rec.stop()
          setIsRecording(false)
        }
      } catch {}
      isSpaceHeldRef.current = false
    }

    window.addEventListener("keydown", handleKeyDown, { passive: false })
    window.addEventListener("keyup", handleKeyUp, { passive: false })
    return () => {
      window.removeEventListener("keydown", handleKeyDown as any)
      window.removeEventListener("keyup", handleKeyUp as any)
    }
  }, [])

  // 同步 isMuted 到 ref，避免 ondataavailable 闭包中取到过期值
  useEffect(() => {
    isMutedRef.current = isMuted
    // 同步更新本地音轨的启用状态，达到真正静音/恢复
    const ms = mediaStreamRef.current
    if (ms) {
      ms.getAudioTracks().forEach((track) => {
        track.enabled = !isMuted
      })
    }
  }, [isMuted])

  // 当 AI 播放时强制静音；播放结束后自动解除静音
  useEffect(() => {
    if (isPlaying) {
      setIsMuted(true)
    } else {
      setIsMuted(false)
    }
  }, [isPlaying])

  // 播放控制、排队处理已在 useVoiceStream 内部管理

  return (
    <Box
      position="relative"
      w="100vw"
      h="100vh"
      overflow="hidden"
      bg="gray.900"
    >
      {/* 背景图片（模糊） */}
      <Box
        position="absolute"
        top="0"
        left="0"
        right="0"
        bottom="0"
        backgroundImage={`url('${avatarUrl}')`}
        backgroundSize="cover"
        backgroundPosition="center"
        // backgroundRepeat="no-repeat"
        filter="blur(20px)"
        opacity="0.3"
      />

      <Flex
        direction="column"
        h="100%"
        align="center"
        justify="center"
        p="6"
        position="relative"
        zIndex="1"
      >
        {/* 头像 */}
        <VStack gap="8" align="center">
          <Box
            w="120px"
            h="120px"
            borderRadius="full"
            backgroundImage={`url('${avatarUrl}')`}
            backgroundSize="cover"
            backgroundPosition="center"
            border="4px solid"
            borderColor="whiteAlpha.300"
            boxShadow="0 0 20px rgba(255,255,255,0.3)"
          />

          {/* 音频可视化 */}
          <HStack gap="2" align="end" h="40px">
            {audioLevels.map((level, index) => (
              <Box
                key={index}
                w="4px"
                h={`${level * 100}%`}
                bg="white"
                borderRadius="2px"
                transition="height 0.2s ease-in-out"
                opacity="0.8"
              />
            ))}
          </HStack>

          {/* 通话状态 */}
          <Text
            color="white"
            fontSize="lg"
            fontWeight="medium"
            textAlign="center"
            opacity="0.9"
          >
            正在通话中...
          </Text>

          <Text color="whiteAlpha.800" fontSize="sm">
            {isRecording ? "录音中（松开空格发送）" : "按住空格开始说话"}
          </Text>

          {/* 控制按钮 */}
          <HStack gap="6" mt="8">
            {/* 静音按钮 */}
            <Button
              aria-label="静音"
              size="lg"
              borderRadius="full"
              bg={isMuted ? "red.500" : "whiteAlpha.200"}
              color="white"
              _hover={{
                bg: isMuted ? "red.600" : "whiteAlpha.300",
                transform: "scale(1.05)",
              }}
              transition="all 0.2s"
              // AI 播放期间强制静音，且不可点击
              disabled={isPlaying}
              onClick={() => setIsMuted(!isMuted)}
              p="4"
            >
              {isMuted ? (
                <FaMicrophoneSlash size="24" />
              ) : (
                <FaMicrophone size="24" />
              )}
            </Button>

            {/* 挂断按钮 */}
            <Button
              aria-label="挂断"
              size="lg"
              borderRadius="full"
              bg="red.500"
              color="white"
              _hover={{
                bg: "red.600",
                transform: "scale(1.05)",
              }}
              transition="all 0.2s"
              p="4"
              onClick={() => {
                // 挂断时：停止录音、关闭音轨、清空播放与待处理队列
                try {
                  if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current)
                  const rec = recorderRef.current
                  if (rec && rec.state !== "inactive") rec.stop()
                } catch {}
                const ms = mediaStreamRef.current
                ms?.getTracks().forEach((t) => t.stop())
                recorderRef.current = null
                mediaStreamRef.current = null
                analyserRef.current = null
                // 停止播放并清理队列
                teardown()
                // 跳转回会话页
                navigate({ to: "/$id", params: { id: id } })
              }}
            >
              <FaPhoneSlash size="24" />
            </Button>
          </HStack>
        </VStack>
      </Flex>
    </Box>
  )
}
