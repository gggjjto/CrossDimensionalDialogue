import { Flex } from "@chakra-ui/react"
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { SelfAgentProvider } from "@/contexts/SelfAgentContext"
import NotFound from "@/components/Common/NotFound"

export const Route = createFileRoute("/create-agent/_layout")({
  component: RouteComponent,
  notFoundComponent: () => <NotFound />,
  beforeLoad: async () => {
    const isAuthenticated = localStorage.getItem("access_token")
    if (!isAuthenticated) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function RouteComponent() {
  return (
    <SelfAgentProvider>
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
    </SelfAgentProvider>
  )
}
