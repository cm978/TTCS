import { defineStore } from "pinia";

import {
  addTaskParticipant,
  createProjectTask,
  createSubtask,
  createWorkLog as createWorkLogApi,
  getTaskDetail,
  listProjectTasks,
  resolveBlocker as resolveBlockerApi,
  updateSubtask,
  updateTask as updateTaskApi
} from "../api/tasks";
import type {
  BlockerResolvePayload,
  Subtask,
  TaskBoardCard,
  TaskCreatePayload,
  TaskDetail,
  TaskStatus,
  TaskUpdatePayload,
  WorkLogCreatePayload
} from "../types/task";

interface TaskState {
  tasksByProject: Record<number, TaskBoardCard[]>;
  activeTask: TaskDetail | null;
  drawerTaskId: number | null;
  loading: boolean;
  saving: boolean;
  error: string | null;
}

function taskError(fallback: string): string {
  return fallback;
}

export const useTaskStore = defineStore("task", {
  state: (): TaskState => ({
    tasksByProject: {},
    activeTask: null,
    drawerTaskId: null,
    loading: false,
    saving: false,
    error: null
  }),
  getters: {
    tasksForProject:
      (state) =>
      (projectId: number): TaskBoardCard[] =>
        state.tasksByProject[projectId] ?? [],
    tasksByStatus:
      (state) =>
      (projectId: number, status: TaskStatus): TaskBoardCard[] =>
        (state.tasksByProject[projectId] ?? []).filter((task) => task.status === status)
  },
  actions: {
    openDrawer(taskId: number) {
      this.drawerTaskId = taskId;
    },
    closeDrawer() {
      this.drawerTaskId = null;
    },
    async loadProjectTasks(projectId: number) {
      this.loading = true;
      this.error = null;
      try {
        const tasks = await listProjectTasks(projectId);
        this.tasksByProject[projectId] = tasks;
        return tasks;
      } catch {
        this.error = taskError("项目任务加载失败，请稍后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async loadTaskDetail(taskId: number) {
      this.loading = true;
      this.error = null;
      try {
        this.activeTask = await getTaskDetail(taskId);
        return this.activeTask;
      } catch {
        this.error = taskError("任务加载失败，请稍后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async createTask(projectId: number, payload: TaskCreatePayload) {
      this.saving = true;
      this.error = null;
      try {
        const task = await createProjectTask(projectId, payload);
        await this.loadProjectTasks(projectId);
        this.activeTask = task;
        return task;
      } catch {
        this.error = taskError("任务创建失败，请检查字段后重试。");
        throw new Error(this.error);
      } finally {
        this.saving = false;
      }
    },
    async updateTask(taskId: number, payload: TaskUpdatePayload) {
      this.saving = true;
      this.error = null;
      try {
        const task = await updateTaskApi(taskId, payload);
        this.activeTask = task;
        await this.loadProjectTasks(task.project_id);
        return task;
      } catch {
        this.error = taskError("任务保存失败，请检查字段后重试。");
        throw new Error(this.error);
      } finally {
        this.saving = false;
      }
    },
    async addParticipant(taskId: number, userId: number) {
      await addTaskParticipant(taskId, userId);
      return this.loadTaskDetail(taskId);
    },
    async addSubtask(taskId: number, title: string): Promise<Subtask> {
      const subtask = await createSubtask(taskId, title);
      await this.loadTaskDetail(taskId);
      if (this.activeTask) {
        await this.loadProjectTasks(this.activeTask.project_id);
      }
      return subtask;
    },
    async toggleSubtask(taskId: number, subtask: Subtask, isCompleted: boolean) {
      const updated = await updateSubtask(taskId, subtask.id, { is_completed: isCompleted });
      await this.loadTaskDetail(taskId);
      if (this.activeTask) {
        await this.loadProjectTasks(this.activeTask.project_id);
      }
      return updated;
    },
    async createWorkLog(taskId: number, payload: WorkLogCreatePayload) {
      this.saving = true;
      try {
        const log = await createWorkLogApi(taskId, payload);
        const task = await this.loadTaskDetail(taskId);
        await this.loadProjectTasks(task.project_id);
        return log;
      } catch {
        this.error = taskError("工作日志保存失败，请检查字段后重试。");
        throw new Error(this.error);
      } finally {
        this.saving = false;
      }
    },
    async resolveBlocker(taskId: number, logId: number, payload: BlockerResolvePayload) {
      this.saving = true;
      try {
        const log = await resolveBlockerApi(taskId, logId, payload);
        const task = await this.loadTaskDetail(taskId);
        await this.loadProjectTasks(task.project_id);
        return log;
      } catch {
        this.error = taskError("解除阻塞失败，请填写处理说明后重试。");
        throw new Error(this.error);
      } finally {
        this.saving = false;
      }
    }
  }
});
