import { Flex } from "@chakra-ui/react"
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/create-agent/_layout")({
  component: RouteComponent,
  beforeLoad: async () => {
    // TODO: 实现真正的鉴权逻辑
    // 现在先暂时允许访问，避免无限重定向
    const isAuthenticated = true // 临时设置为 true
    if (!isAuthenticated) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function RouteComponent() {
  return (
    <Flex
      h={"100vh"}
      w={"full"}
      alignItems={"center"}
      justifyContent={"center"}
      px={4}
      bg={"bg.muted"}
    >
      <Outlet />
    </Flex>
  )
}
