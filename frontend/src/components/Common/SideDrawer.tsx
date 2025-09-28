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
import { BsChat } from "react-icons/bs"
import Divide from "../ui/divide"
import { Button } from "../ui/button"
import { useNavigate } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import { conversationsApi } from "@/api/conversations"
import type { ConversationWithDetails } from "@/api/conversations/type"
import { useUserInfo } from "@/hooks/query/useUserInfo"

// 侧边抽屉：展示用户信息与最近会话

type SideDrawerProps = {
  isOpen: boolean
  onClose: () => void
}

export default function SideDrawer({ isOpen, onClose }: SideDrawerProps) {
  const navigate = useNavigate()
  const user = useUserInfo()
  const [recent, setRecent] = useState<ConversationWithDetails[]>([])

  useEffect(() => {
    if (!isOpen) return
    ;(async () => {
      try {
        const res = await conversationsApi.getConversations({ skip: 0, limit: 10 })
        setRecent(res.conversations || [])
      } catch {
        setRecent([])
      }
    })()
  }, [isOpen])

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
            <Box w={"100%"} px={6} py={2} onClick={() => { navigate({ to: "/user" }); onClose() }}>
              <HStack gap="2">
                <Avatar.Root>
                  <Avatar.Image src={user?.avatar_url || "/assets/images/agent.png"} />
                  <Avatar.Fallback name={user?.full_name || user?.email} />
                </Avatar.Root>
                <Stack gap="0">
                  <Text fontWeight="medium">{user?.full_name || user?.email}</Text>
                  <Text color="fg.muted" textStyle="sm">{user?.email}</Text>
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
                onClick={() => { navigate({ to: "/create-agent" }); onClose() }}
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
                onClick={() => { navigate({ to: "/" }); onClose() }}
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
                {recent.map((cv) => (
                  <Button
                    key={cv.id}
                    w={"100%"}
                    h={16}
                    variant="ghost"
                    justifyContent="flex-start"
                    _hover={{ bg: "bg.active" }}
                    onClick={() => { navigate({ to: "/$id", params: { id: cv.id } }); onClose() }}
                  >
                    <HStack gap="3" w="100%">
                      <Avatar.Root size="sm">
                        <Avatar.Image src={cv.character?.avatar_url || "/assets/images/agent.png"} />
                        <Avatar.Fallback name={cv.character?.name || cv.title} />
                      </Avatar.Root>
                      <Stack gap="0" align="start" flex="1">
                        <Text fontWeight="medium" textStyle="sm">
                          {cv.character?.name || cv.title}
                        </Text>
                        <Text
                          color="fg.muted"
                          textStyle="xs"
                          overflow="hidden"
                          textOverflow="ellipsis"
                          whiteSpace="nowrap"
                          fontWeight="normal"
                        >
                          {cv.description || "点击继续对话"}
                        </Text>
                      </Stack>
                      <BsChat className="text-muted" />
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
