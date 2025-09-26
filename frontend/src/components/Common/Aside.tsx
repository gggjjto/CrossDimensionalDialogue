import { Avatar, Box, HStack, Stack, Text } from "@chakra-ui/react"
import { IoMdAdd } from "react-icons/io"
import { HiOutlineHome } from "react-icons/hi"
import { BsChat } from "react-icons/bs"

import Divide from "../ui/divide"
import { Button } from "../ui/button"
import { useNavigate } from "@tanstack/react-router"

const chatedAgents = [
  {
    name: "小助手",
    description: "有什么我可以帮助你的吗？",
  },
  {
    name: "苏格拉底",
    description: "我是苏格拉底，有什么我可以帮助你的吗？",
  },
  {
    name: "李大明",
    description: "我是李大明，有什么我可以帮助你的吗？",
  },
]

export default function IndexAside() {
  const navigate = useNavigate()

  return (
    <Box
      maxW={"20%"}
      bg="bg.muted"
      py="4"
      display="flex"
      flexDirection="column"
      alignItems={"center"}
      gap="8"
      borderRightWidth="1px"
      borderColor="border.default"
      h={"full"}
    >
      <Box w={"100%"} px={6} py={2}>
        <HStack gap="2">
          <Avatar.Root>
            <Avatar.Fallback name={"张小明"} />
            <Avatar.Image />
          </Avatar.Root>
          <Stack gap="0">
            <Text fontWeight="medium">{"张小明"}</Text>
            <Text color="fg.muted" textStyle="sm">
              {"zhang@example.com"}
            </Text>
          </Stack>
        </HStack>
      </Box>

      <Divide />

      <Box w={"90%"} spaceY={2}>
        <Button
          w={"100%"}
          h={14}
          variant="outline"
          bg={"white"}
          _hover={{ bg: "bg.muted" }}
          transition={"all 0.2s ease-in-out"}
          size="lg"
          onClick={() => navigate({ to: "/create-agent" })}
        >
          <IoMdAdd />
          创建智能体
        </Button>

        <Box
          w={"100%"}
          h={10}
          display={"flex"}
          alignItems={"center"}
          bg={"bg.active"}
          padding={2}
          borderRadius={"md"}
          spaceX={2}
        >
          <HiOutlineHome display={"inline-block"} />
          <Text>探索发现</Text>
        </Box>

        <Box spaceY={2} paddingTop={7}>
          <Divide thickness="2px" color="border.default" />

          <Text color={"fg.muted"} paddingBottom={3}>
            最近聊天
          </Text>

          <Stack spaceY={2}>
            {chatedAgents.map((agent) => (
              <Box
                display={"flex"}
                alignItems={"center"}
                justifyContent={"space-between"}
                _hover={{ bg: "bg.active" }}
                cursor={"pointer"}
                padding={2}
                borderRadius={"md"}
                transition={"all 0.2s ease-in-out"}
              >
                <HStack gap="2">
                  <Avatar.Root>
                    <Avatar.Fallback name={agent.name} />
                    <Avatar.Image />
                  </Avatar.Root>
                  <Stack gap="0">
                    <Text fontWeight="medium">{agent.name}</Text>
                    <Text color="fg.muted" textStyle="xs">
                      {agent.description}
                    </Text>
                  </Stack>
                </HStack>

                <BsChat className="text-muted" />
              </Box>
            ))}
          </Stack>
        </Box>
      </Box>
    </Box>
  )
}
