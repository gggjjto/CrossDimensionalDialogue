import { Button } from "@/components/ui/button"
import { Box, Center, Text } from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { GoArrowLeft } from "react-icons/go"
import { LuArrowRight } from "react-icons/lu"

export const Route = createFileRoute("/create-agent/")({
  component: RouteComponent,
})

const sources = [
  {
    label: "IP",
    value: "ip",
    description: "一键点击，创建热门角色~",
  },
  {
    label: "自创",
    value: "self",
    description: "角色还停留在想象？\n快点击这里，创建你心目中的角色",
  },
]

function RouteComponent() {
  const navigate = useNavigate()
  const [selectedSource, setSelectedSource] = useState<string | null>(null)

  return (
    <Center h={"100vh"} p={4} position={"relative"} w={"full"}>
      {/* 返回主页 */}
      <Box
        position={"absolute"}
        top={4}
        left={4}
        display={"flex"}
        gap={2}
        alignItems={"center"}
        onClick={() => navigate({ to: "/" })}
        cursor="pointer"
      >
        <GoArrowLeft /> 返回主页
      </Box>

      <Box spaceY={10}>
        <Text fontWeight={550} textAlign={"center"} fontSize={"5xl"}>
          请选择角色来源
        </Text>

        <Box display={"flex"} gap={4}>
          {sources.map((source) => {
            const isSelected = selectedSource === source.value

            return (
              <Box
                key={source.label}
                display={"flex"}
                justifyContent={"center"}
                alignItems={"center"}
                flexDirection={"column"}
                gap={2}
                height={"250px"}
                width={"250px"}
                border={isSelected ? "2px solid" : "2px solid"}
                borderColor={isSelected ? "accent.default" : "border.default"}
                borderRadius={"md"}
                padding={4}
                cursor={"pointer"}
                transition={"all 0.2s ease-in-out"}
                _hover={{ bg: "bg.muted" }}
                onClick={() => {
                  if (isSelected) {
                    setSelectedSource(null)
                  } else {
                    setSelectedSource(source.value)
                  }
                }}
              >
                <Text fontWeight={550} fontSize={"2xl"}>
                  {source.label}
                </Text>
                <Text color={"fg.muted"}>{source.description}</Text>
              </Box>
            )
          })}
        </Box>

        <Button
          w={"full"}
          disabled={!selectedSource}
          onClick={() => {
            navigate({ to: `/create-agent/${selectedSource}` })
          }}
        >
          继续 <LuArrowRight style={{ marginLeft: 4 }} />
        </Button>
      </Box>
    </Center>
  )
}
