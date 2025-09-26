import { useEffect, useRef } from "react"
import { Box, VStack, Textarea, HStack, IconButton } from "@chakra-ui/react"
import { LuPhone, LuSend } from "react-icons/lu"
import { GrMicrophone } from "react-icons/gr"
import { useNavigate, useParams } from "@tanstack/react-router"

type ChatInputProps = {
  value: string
  onChange: (value: string) => void
  onSend: VoidFunction
  onVoiceClick?: VoidFunction
  placeholder?: string
  minHeightPx?: number
  maxHeightPx?: number
}

export default function ChatInput({
  value,
  onChange,
  onSend,
  onVoiceClick,
  placeholder = "发送消息",
  minHeightPx = 40,
  maxHeightPx = 200,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const navigate = useNavigate()
  const { id } = useParams({ from: "/$id/_layout" })

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (!textarea) return
    textarea.style.height = "auto"
    const newHeight = Math.min(
      Math.max(textarea.scrollHeight, minHeightPx),
      maxHeightPx
    )
    textarea.style.height = `${newHeight}px`
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [value, minHeightPx, maxHeightPx])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (value.trim()) onSend()
    }
  }

  return (
    <Box
      border="1px solid rgba(255,255,255,0.2)"
      borderRadius="xl"
      bg="rgba(0,0,0,0.2)"
      p="3"
      w={"100%"}
    >
      <VStack align="stretch" gap="3" w={"100%"}>
        <Textarea
          ref={textareaRef}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          bg="transparent"
          border="none"
          color="white"
          _placeholder={{ color: "rgba(255,255,255,0.6)" }}
          _focus={{ outline: "none" }}
          resize="none"
          minH={`${minHeightPx}px`}
          maxH={`${maxHeightPx}px`}
          rows={1}
          css={{
            "&::-webkit-scrollbar": {
              width: "6px",
              margin: "4px",
            },
            "&::-webkit-scrollbar-track": {
              width: "6px",
              margin: "4px",
              background: "transparent",
            },
            "&::-webkit-scrollbar-thumb": {
              background: "rgba(255,255,255,0.3)",
              borderRadius: "3px",
              margin: "4px",
            },
            "&::-webkit-scrollbar-thumb:hover": {
              background: "rgba(255,255,255,0.5)",
            },
          }}
        />

        <HStack justify={"space-between"} w={"100%"}>
          <IconButton
            aria-label="语音"
            variant="ghost"
            color="accent.foreground"
            size="sm"
            border={"1px solid rgba(255,255,255,0.2)"}
            onClick={() => {
              navigate({ to: "/$id/phone", params: { id: id } })
            }}
            _hover={{ bg: "rgba(255,255,255,0.1)" }}
          >
            <LuPhone />
          </IconButton>

          <HStack gap={2}>
            <IconButton
              aria-label="语音"
              variant="ghost"
              color="accent.foreground"
              size="sm"
              border={"1px solid rgba(255,255,255,0.2)"}
              onClick={onVoiceClick}
              _hover={{ bg: "rgba(255,255,255,0.1)" }}
            >
              <GrMicrophone />
            </IconButton>
            <IconButton
              aria-label="发送"
              variant="ghost"
              color="accent.foreground"
              size="sm"
              bg={value.trim() ? "accent.default" : "transparent"}
              border={"1px solid rgba(255,255,255,0.2)"}
              disabled={!value.trim()}
              _hover={{ bg: "rgba(255,255,255,0.1)" }}
              onClick={onSend}
            >
              <LuSend />
            </IconButton>
          </HStack>
        </HStack>
      </VStack>
    </Box>
  )
}
