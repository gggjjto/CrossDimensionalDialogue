import {
  createFileRoute,
  redirect,
  useNavigate,
  useParams,
} from "@tanstack/react-router"
import { Box, Flex, VStack, HStack, Text, Button } from "@chakra-ui/react"
import { FaPhoneSlash, FaMicrophone, FaMicrophoneSlash } from "react-icons/fa"
import { useState, useEffect, useRef } from "react"
import { voiceApi } from "@/api/voice"
import { tasksApi } from "@/api/tasks"

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
  const [audioLevels, setAudioLevels] = useState([0.3, 0.6, 0.4, 0.8, 0.5])
  const [autoPlay, setAutoPlay] = useState(true)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioQueueRef = useRef<string[]>([])
  const playingRef = useRef<boolean>(false)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const rafIdRef = useRef<number | null>(null)
  // 任务顺序处理队列
  const pendingChunksRef = useRef<string[]>([])
  const processingRef = useRef<boolean>(false)

  const navigate = useNavigate()
  const { id } = useParams({ from: "/$id/_layout" })

  // 启动麦克风录音（分段上传）
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
          try {
            const file = new File([blob], `chunk_${Date.now()}.webm`, {
              type: blob.type || "audio/webm",
            })
            const up = await voiceApi.uploadAudio(file)
            // 限流：队列过长时丢弃最新片段，避免排队过久
            if (pendingChunksRef.current.length >= 3 && processingRef.current) {
              return
            }
            pendingChunksRef.current.push(up.audio_url)
            maybeStartProcessor()
          } catch {
            // 忽略错误以保持通话流畅
          }
        }
        // 缩短分片大小，提升响应（~1.2s）
        recorder.start(1200)
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

  // 同步 isMuted 到 ref，避免 ondataavailable 闭包中取到过期值
  useEffect(() => {
    isMutedRef.current = isMuted
  }, [isMuted])

  const enqueueAudio = (url: string) => {
    audioQueueRef.current.push(url)
    if (!playingRef.current && autoPlay) playNext()
  }

  const maybeStartProcessor = () => {
    if (processingRef.current) return
    processingRef.current = true
    ;(async () => {
      const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))
      try {
        while (pendingChunksRef.current.length > 0) {
          const url = pendingChunksRef.current.shift()!
          try {
            const task = await voiceApi.processVoiceMessage({
              conversation_id: id,
              audio_file_url: url,
            })
            let tries = 0
            const maxTries = 30
            while (tries < maxTries) {
              const t = await tasksApi.getTask(task.task_id)
              if (t.status === "COMPLETED") {
                const a = t.result?.audio_url as string | undefined
                if (a) enqueueAudio(a)
                break
              }
              if (t.status !== "PENDING" && t.status !== "PROCESSING") break
              tries += 1
              await delay(600)
            }
          } catch {
            // 略过该分片
          }
          // 片间间隙，避免打爆后台
          await delay(150)
        }
      } finally {
        processingRef.current = false
        // 若期间又有新分片进入，继续处理
        if (pendingChunksRef.current.length > 0) {
          maybeStartProcessor()
        }
      }
    })()
  }

  const playNext = () => {
    if (!audioRef.current) audioRef.current = new Audio()
    const audio = audioRef.current
    const next = audioQueueRef.current.shift()
    if (!next) {
      playingRef.current = false
      return
    }
    playingRef.current = true
    audio.src = next
    audio.onended = () => {
      playingRef.current = false
      playNext()
    }
    audio.play().catch(() => {
      playingRef.current = false
    })
  }

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
        backgroundImage="url('/assets/images/agent.png')"
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
            backgroundImage="url('/assets/images/agent.png')"
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

          {/* 控制按钮 */}
          <HStack gap="6" mt="8">
            {/* 自动播放开关 */}
            <Button
              aria-label="自动播放语音"
              size="lg"
              borderRadius="full"
              bg={autoPlay ? "green.500" : "whiteAlpha.200"}
              color="white"
              _hover={{
                bg: autoPlay ? "green.600" : "whiteAlpha.300",
                transform: "scale(1.05)",
              }}
              transition="all 0.2s"
              onClick={() => setAutoPlay((v) => !v)}
              p="4"
            >
              {autoPlay ? "自动播放：开" : "自动播放：关"}
            </Button>

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
              onClick={() => navigate({ to: "/$id", params: { id: id } })}
            >
              <FaPhoneSlash size="24" />
            </Button>
          </HStack>
        </VStack>
      </Flex>
    </Box>
  )
}
