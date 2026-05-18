import { apiClient } from "./client";
import type {
  BlockerResolvePayload,
  Subtask,
  TaskBoardCard,
  TaskCreatePayload,
  TaskDependency,
  TaskDetail,
  TaskParticipant,
  TaskUpdatePayload,
  WorkLog,
  WorkLogCreatePayload,
  WorkLogUpdatePayload
} from "../types/task";

export async function listProjectTasks(projectId: number): Promise<TaskBoardCard[]> {
  const { data } = await apiClient.get<TaskBoardCard[]>(`/projects/${projectId}/tasks`);
  return data;
}

export async function createProjectTask(projectId: number, payload: TaskCreatePayload): Promise<TaskDetail> {
  const { data } = await apiClient.post<TaskDetail>(`/projects/${projectId}/tasks`, payload);
  return data;
}

export async function getTaskDetail(taskId: number): Promise<TaskDetail> {
  const { data } = await apiClient.get<TaskDetail>(`/tasks/${taskId}`);
  return data;
}

export async function updateTask(taskId: number, payload: TaskUpdatePayload): Promise<TaskDetail> {
  const { data } = await apiClient.patch<TaskDetail>(`/tasks/${taskId}`, payload);
  return data;
}

export async function deleteTask(taskId: number): Promise<void> {
  await apiClient.delete(`/tasks/${taskId}`);
}

export async function addTaskParticipant(taskId: number, userId: number): Promise<TaskParticipant> {
  const { data } = await apiClient.post<TaskParticipant>(`/tasks/${taskId}/participants`, { user_id: userId });
  return data;
}

export async function removeTaskParticipant(taskId: number, userId: number): Promise<TaskParticipant> {
  const { data } = await apiClient.delete<TaskParticipant>(`/tasks/${taskId}/participants/${userId}`);
  return data;
}

export async function createSubtask(taskId: number, title: string): Promise<Subtask> {
  const { data } = await apiClient.post<Subtask>(`/tasks/${taskId}/subtasks`, { title });
  return data;
}

export async function updateSubtask(taskId: number, subtaskId: number, payload: Partial<Subtask>): Promise<Subtask> {
  const { data } = await apiClient.patch<Subtask>(`/tasks/${taskId}/subtasks/${subtaskId}`, payload);
  return data;
}

export async function addTaskDependency(taskId: number, dependsOnTaskId: number): Promise<TaskDependency> {
  const { data } = await apiClient.post<TaskDependency>(`/tasks/${taskId}/dependencies`, {
    depends_on_task_id: dependsOnTaskId
  });
  return data;
}

export async function createWorkLog(taskId: number, payload: WorkLogCreatePayload): Promise<WorkLog> {
  const { data } = await apiClient.post<WorkLog>(`/tasks/${taskId}/work-logs`, payload);
  return data;
}

export async function updateWorkLog(taskId: number, logId: number, payload: WorkLogUpdatePayload): Promise<WorkLog> {
  const { data } = await apiClient.patch<WorkLog>(`/tasks/${taskId}/work-logs/${logId}`, payload);
  return data;
}

export async function resolveBlocker(taskId: number, logId: number, payload: BlockerResolvePayload): Promise<WorkLog> {
  const { data } = await apiClient.post<WorkLog>(`/tasks/${taskId}/work-logs/${logId}/resolve-blocker`, payload);
  return data;
}
