import { Flex } from "@chakra-ui/react"
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    const isAuthenticated = localStorage.getItem("access_token")
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
