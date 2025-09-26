import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

import NotFound from "@/components/Common/NotFound"

export const Route = createFileRoute("/$id/_layout")({
  component: RouteComponent,
  notFoundComponent: () => <NotFound />,
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
  return <Outlet />
}
