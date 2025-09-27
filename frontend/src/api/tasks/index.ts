import { request } from "@/utils/request"

export type TaskStatus =
  | "PENDING"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "TIMEOUT"

export interface TaskResponse {
  id: string
  status: TaskStatus
  progress: number
  result?: {
    character_response?: string
    audio_url?: string
    [key: string]: unknown
  }
}

export const tasksApi = {
  getTask: async (taskId: string) => {
    return request.get<TaskResponse>(`/v1/tasks/${taskId}`)
  },
}


