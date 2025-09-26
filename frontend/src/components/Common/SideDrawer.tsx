import {
  DrawerRoot,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
  DrawerCloseTrigger,
} from "../ui/drawer"
import { Avatar, Box, HStack, Stack, Text } from "@chakra-ui/react"
import { IoMdAdd } from "react-icons/io"
import { HiOutlineHome } from "react-icons/hi"
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

type SideDrawerProps = {
  isOpen: boolean
  onClose: () => void
}

export default function SideDrawer({ isOpen, onClose }: SideDrawerProps) {
  const navigate = useNavigate()

  return (
    <DrawerRoot
      placement="start"
      open={isOpen}
      onOpenChange={(e) => !e.open && onClose()}
      size={"sm"}
    >
      <DrawerContent bg="bg.default">
        <DrawerCloseTrigger />
        <DrawerHeader borderBottomWidth="1px">菜单</DrawerHeader>
        <DrawerBody p="0">
          <Box
            bg="bg.muted"
            py="4"
            display="flex"
            flexDirection="column"
            alignItems={"center"}
            gap="8"
            h={"full"}
            w="100%"
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
                _hover={{ bg: "bg.active" }}
                onClick={() => navigate({ to: "/create-agent" })}
              >
                <HStack gap="2">
                  <IoMdAdd />
                  <Text>创建智能体</Text>
                </HStack>
              </Button>
            </Box>

            <Box w={"90%"} spaceY={2}>
              <Button
                w={"100%"}
                p={"6px 4px"}
                variant="ghost"
                _hover={{ bg: "accent.octonary" }}
                justifyContent="flex-start"
                onClick={() => navigate({ to: "/" })}
              >
                <HStack gap="2">
                  <HiOutlineHome />
                  <Text>探索发现</Text>
                </HStack>
              </Button>
            </Box>

            <Box w={"90%"}>
              <Text textStyle="sm" color="fg.muted" mb={4}>
                最近聊天
              </Text>
              <Stack gap="2">
                {chatedAgents.map((agent, index) => (
                  <Button
                    key={index}
                    w={"100%"}
                    h={16}
                    variant="ghost"
                    justifyContent="flex-start"
                    _hover={{ bg: "bg.active" }}
                    onClick={() => navigate({ to: `/${index + 1}` })}
                  >
                    <HStack gap="3" w="100%">
                      <Avatar.Root size="sm">
                        <Avatar.Fallback name={agent.name} />
                        <Avatar.Image />
                      </Avatar.Root>
                      <Stack gap="0" align="start" flex="1">
                        <Text fontWeight="medium" textStyle="sm">
                          {agent.name}
                        </Text>
                        <Text
                          color="fg.muted"
                          textStyle="xs"
                          overflow="hidden"
                          textOverflow="ellipsis"
                          whiteSpace="nowrap"
                          fontWeight="normal"
                        >
                          {agent.description}
                        </Text>
                      </Stack>
                    </HStack>
                  </Button>
                ))}
              </Stack>
            </Box>
          </Box>
        </DrawerBody>
      </DrawerContent>
    </DrawerRoot>
  )
}
