import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/create-agent/_layout/self-result')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/create-agent/_layout/self-result"!</div>
}
