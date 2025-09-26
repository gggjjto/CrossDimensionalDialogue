import { Box, Flex, Image, Text } from "@chakra-ui/react"
import { useState, useEffect } from "react"

interface AgentCardProps {
  title: string
  slogan: string
  tags?: string[]
  imageSrc: string
}

export default function AgentCard({ title, slogan, tags = [], imageSrc }: AgentCardProps) {
  const [dominantColor, setDominantColor] = useState("bg.muted") // 默认颜色
  const [textColor, setTextColor] = useState("fg.default") // 默认文字颜色

  // 提取图片主色调的函数
  const extractDominantColor = (imageSrc: string) => {
    const img = document.createElement('img') as HTMLImageElement
    img.crossOrigin = "anonymous"
    
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        
        if (!ctx) return
        
        // 设置canvas尺寸
        canvas.width = 50
        canvas.height = 50
        
        // 绘制图片到canvas
        ctx.drawImage(img, 0, 0, 50, 50)
        
        // 获取像素数据
        const imageData = ctx.getImageData(0, 0, 50, 50)
        const data = imageData.data
        
        // 计算平均颜色
        let r = 0, g = 0, b = 0
        let count = 0
        
        for (let i = 0; i < data.length; i += 4) {
          r += data[i]
          g += data[i + 1]
          b += data[i + 2]
          count++
        }
        
        r = Math.floor(r / count)
        g = Math.floor(g / count)
        b = Math.floor(b / count)
        
        // 转换为十六进制
        const hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
        
        // 计算亮度来决定文字颜色
        const brightness = (r * 299 + g * 587 + b * 114) / 1000
        const textColor = brightness > 128 ? "fg.default" : "fg.default"
        
        setDominantColor(hexColor)
        setTextColor(textColor)
      } catch (error) {
        console.log("颜色提取失败，使用默认颜色")
      }
    }
    
    img.onerror = () => {
      console.log("图片加载失败，使用默认颜色")
    }
    
    img.src = imageSrc
  }

  useEffect(() => {
    extractDominantColor(imageSrc)
  }, [imageSrc])

  return (
    <Box
      bg="surface.default"
      borderRadius="lg"
      border="1px solid"
      borderColor="border.default"
      shadow="sm"
      overflow="hidden"
      h="160px"
      w="675px"
    >
      <Flex h="full">
        {/* 左侧图片区域 */}
        <Box w="25%" h="full" position="relative" overflow="hidden" bg="bg.muted">
          <Image
            src={imageSrc}
            alt={title}
            w="full"
            h="full"
            objectFit="cover"
            objectPosition="center"
          />
          {/* 左右模糊边界遮罩 */}
          <Box
            position="absolute"
            top={0}
            left={0}
            w="25px"
            h="full"
            bgGradient="linear(to-r, rgba(255,255,255,1), rgba(255,255,255,0.7), rgba(255,255,255,0.3), transparent)"
            pointerEvents="none"
            zIndex={1}
            css={{
              backdropFilter: "blur(2px)",
              WebkitBackdropFilter: "blur(2px)"
            }}
          />
          <Box
            position="absolute"
            top={0}
            right={0}
            w="25px"
            h="full"
            bgGradient="linear(to-l, rgba(255,255,255,1), rgba(255,255,255,0.7), rgba(255,255,255,0.3), transparent)"
            pointerEvents="none"
            zIndex={1}
            css={{
              backdropFilter: "blur(2px)",
              WebkitBackdropFilter: "blur(2px)"
            }}
          />
        </Box>

        {/* 右侧信息区域 */}
        <Box 
          w="75%" 
          bg={dominantColor} 
          p={4} 
          display="flex" 
          flexDirection="column" 
          justifyContent="space-between"
          position="relative"
        >
          {/* 半透明遮罩层，确保文字可读性 */}
          <Box
            position="absolute"
            top={0}
            left={0}
            right={0}
            bottom={0}
            bg="rgba(255,255,255,0.1)"
            pointerEvents="none"
          />
          <Box position="relative" zIndex={1}>
            <Text fontSize="lg" fontWeight="bold" color={textColor} mb={2} textAlign="center">
              {title}
            </Text>
            <Box w="100%" h="1px" bg={textColor} opacity={0.3} mb={2} />
            <Text fontSize="sm" color={textColor} opacity={0.8} textAlign="center">
              {slogan}
            </Text>
          </Box>
          
          {/* 标签区域 */}
          {tags.length > 0 && (
            <Flex flexWrap="wrap" gap={2} position="relative" zIndex={1}>
              {tags.slice(0, 4).map((tag, index) => (
                <Box
                  key={index}
                  bg="rgba(255,255,255,0.2)"
                  borderRadius="md"
                  px={3}
                  py={1}
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.3)"
                  backdropFilter="blur(10px)"
                >
                  <Text fontSize="xs" color={textColor}>
                    {tag}
                  </Text>
                </Box>
              ))}
              {tags.length > 4 && (
                <Text fontSize="xs" color={textColor} opacity={0.7} px={2}>
                  +{tags.length - 4}
                </Text>
              )}
            </Flex>
          )}
        </Box>
      </Flex>
    </Box>
  )
}
