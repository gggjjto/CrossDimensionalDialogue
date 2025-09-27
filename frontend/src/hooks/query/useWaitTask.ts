import { useEffect, useRef } from "react"
import { tasksApi, type TaskStatus } from "@/api/tasks"

/**
 * 轻量轮询等待任务到达终态（非 React Query 版）
 * - 适用于需要手动队列/顺序控制的场景（如电话分片串行）
 * - 返回一个 wait(taskId, {intervalMs, maxTries}) Promise，resolve 为最终任务数据
 */
export const useWaitTask = () => {
  const isMountedRef = useRef(true)

  useEffect(() => {
    return () => {
      isMountedRef.current = false
    }
  }, [])

  const TERMINAL: TaskStatus[] = ["COMPLETED", "FAILED", "CANCELLED", "TIMEOUT"]

  const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))

  const wait = async (
    taskId: string,
    opts?: { intervalMs?: number; maxTries?: number }
  ) => {
    const intervalMs = opts?.intervalMs ?? 600
    const maxTries = opts?.maxTries ?? 30
    let tries = 0
    while (isMountedRef.current && tries < maxTries) {
      const t = await tasksApi.getTask(taskId)
      if (TERMINAL.includes(t.status)) return t
      tries += 1
      await delay(intervalMs)
    }
    // 超时也返回最后一次结果（或抛错）。这里选择抛错，便于调用方处理
    throw new Error("Task waiting timeout")
  }

  return { wait }
}
