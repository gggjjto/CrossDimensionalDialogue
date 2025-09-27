import { useQuery } from "@tanstack/react-query"
import { tasksApi, type TaskStatus } from "@/api/tasks"

const TERMINAL: TaskStatus[] = ["COMPLETED", "FAILED", "CANCELLED", "TIMEOUT"]

/**
 * 查询任务状态，并支持轮询直到达到终态
 * - 通过 `refetchIntervalMs` 控制轮询间隔
 */
export const useTask = (
  taskId: string | null | undefined,
  options?: { refetchIntervalMs?: number }
) => {
  const interval = options?.refetchIntervalMs ?? 800

  return useQuery({
    queryKey: ["task", taskId],
    enabled: Boolean(taskId),
    queryFn: async () => {
      if (!taskId) throw new Error("taskId is required")
      return tasksApi.getTask(taskId)
    },
    // 在非终态下执行轮询
    refetchInterval: (q) => {
      const status = (q.state.data as any)?.status as TaskStatus | undefined
      if (!taskId) return false
      if (!status) return interval
      return TERMINAL.includes(status) ? false : interval
    },
  })
}
