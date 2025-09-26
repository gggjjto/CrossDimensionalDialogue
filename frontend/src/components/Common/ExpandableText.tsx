import { useState, useRef, useEffect } from "react"
import { Box, Text, Button, HStack } from "@chakra-ui/react"
import { FaCaretDown } from "react-icons/fa"

interface ExpandableTextProps {
  children: string
  maxLines?: number
  fontSize?: "sm" | "md"
  lineHeight?: string
  color?: string
  buttonColor?: string
  buttonSize?: "sm" | "md" | "lg" | "xs"
}

export default function ExpandableText({
  children,
  maxLines = 1,
  fontSize = "sm",
  lineHeight = "1.6",
  color = "rgba(255,255,255,0.9)",
  buttonColor = "accent.foreground",
  buttonSize = "sm",
}: ExpandableTextProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [showButton, setShowButton] = useState(false)
  const textRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (textRef.current) {
      const lineHeightValue = parseFloat(lineHeight)
      const fontSizeValue = fontSize === "sm" ? 14 : fontSize === "md" ? 16 : 12
      const maxHeight = maxLines * fontSizeValue * lineHeightValue

      // 检查文本是否超过最大行数
      if (textRef.current.scrollHeight > maxHeight) {
        setShowButton(true)
      } else {
        setShowButton(false)
      }
    }
  }, [children, maxLines, fontSize, lineHeight])

  return (
    <Box>
      <Text
        ref={textRef}
        fontSize={fontSize}
        lineHeight={lineHeight}
        color={color}
        overflow="hidden"
        style={{
          display: "-webkit-box",
          WebkitLineClamp: isExpanded ? "none" : maxLines,
          WebkitBoxOrient: "vertical",
          maxHeight: isExpanded ? "none" : `${maxLines * 1.6}em`,
        }}
        transition="max-height 0.3s ease-in-out, opacity 0.3s ease-in-out"
      >
        {children}
      </Text>

      {showButton && (
        <HStack mt="2" gap="1">
          <Button
            variant="ghost"
            color={buttonColor}
            size={buttonSize}
            onClick={() => setIsExpanded(!isExpanded)}
            _hover={{ bg: "rgba(255,255,255,0.1)" }}
            p="1"
            h="auto"
            minW="auto"
            fontSize="xs"
          >
            {isExpanded ? "收起" : "展开"}
          </Button>
          <Box
            transform={isExpanded ? "rotate(180deg)" : "rotate(0deg)"}
            transition="transform 0.2s"
            color={buttonColor}
          >
            <FaCaretDown size={12} />
          </Box>
        </HStack>
      )}
    </Box>
  )
}
