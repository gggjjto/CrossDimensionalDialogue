import { Box, Flex } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import UserProfile from "@/components/user/UserProfile"
import UserTabs from "@/components/user/UserTabs"

export const Route = createFileRoute("/user")({
  component: UserPage,
})

function UserPage() {
  return (
    <Flex h="100vh" bg="bg.default">
      {/* 左侧用户信息区域 - 1/3 宽度 */}
      <Box
        w="33.33%"
        bg="bg.muted"
        borderRightWidth="1px"
        borderColor="border.default"
        p={10}
        overflowY="auto"
        display="flex"
        justifyContent="center"
        alignItems="flex-start"
        pt={150}
      >
        <UserProfile />
      </Box>

      {/* 右侧内容区域 - 2/3 宽度 */}
      <Box w="66.67%" p={0}>
        <UserTabs />
      </Box>
    </Flex>
  )
}
