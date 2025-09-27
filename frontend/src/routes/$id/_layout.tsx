import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

import NotFound from "@/components/Common/NotFound"

export const Route = createFileRoute("/$id/_layout")({
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
  return <Outlet />
}
