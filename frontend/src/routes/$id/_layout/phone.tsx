import { createFileRoute, useNavigate, useParams } from "@tanstack/react-router"
import { Box, Flex, VStack, HStack, Text, Button } from "@chakra-ui/react"
import { FaPhoneSlash, FaMicrophone, FaMicrophoneSlash } from "react-icons/fa"
import { useState, useEffect } from "react"

export const Route = createFileRoute("/$id/_layout/phone")({
  component: RouteComponent,
})

function RouteComponent() {
  const [isMuted, setIsMuted] = useState(false)
  const [audioLevels, setAudioLevels] = useState([0.3, 0.6, 0.4, 0.8, 0.5])

  const navigate = useNavigate()
  const { id } = useParams({ from: "/$id/_layout" })

  // 模拟音频可视化动画
  useEffect(() => {
    const interval = setInterval(() => {
      setAudioLevels((prev) => prev.map(() => Math.random() * 0.8 + 0.2))
    }, 200)

    return () => clearInterval(interval)
  }, [])

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
