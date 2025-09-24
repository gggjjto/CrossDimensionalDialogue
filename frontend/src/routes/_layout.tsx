import { Flex } from "@chakra-ui/react"
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout")({
  component: Layout,
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

function Layout() {
  return (
    <Flex direction="column" h="100vh">
      <Flex flex="1" overflow="hidden" pt={4}>
        <Flex flex="1" direction="column">
          <Outlet />
        </Flex>
      </Flex>
    </Flex>
  )
}

export default Layout
