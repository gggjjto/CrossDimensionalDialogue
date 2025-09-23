import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { CustomProvider } from "./components/ui/provider"
import { routeTree } from "./routeTree.gen"

const queryClient = new QueryClient({
  // TODO: 错误处理
  queryCache: new QueryCache({
    onError: () => {},
  }),
  mutationCache: new MutationCache({
    // TODO: 错误处理
    onError: () => {},
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CustomProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </CustomProvider>
  </StrictMode>
)
