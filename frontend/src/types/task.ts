import type { UserPublic } from "./auth";
import type { BoardColumn } from "./project";

export type TaskStatus = "TODO" | "IN_PROGRESS" | "IN_REVIEW" | "REJECTED" | "DONE" | "CLOSED" | "DELETED";
export type TaskType = "GENERAL" | "DOCUMENT" | "CODE";
export type TaskPriority = "URGENT" | "HIGH" | "MEDIUM" | "LOW";

export interface TaskParticipant {
  id: number;
  task_id: number;
  user_id: number;
  role: "PARTICIPANT";
  removed_at: string | null;
  created_at: string;
  user?: UserPublic | null;
}

export interface Subtask {
  id: number;
  task_id: number;
  title: string;
  is_completed: boolean;
  completed_by_id: number | null;
  completed_at: string | null;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface TaskDependency {
  id: number;
  task_id: number;
  depends_on_task_id: number;
  created_at: string;
}

export interface WorkLog {
  id: number;
  task_id: number;
  user_id: number;
  work_date: string;
  hours: number;
  content: string;
  work_type: string;
  is_blocked: boolean;
  blocked_reason: string | null;
  resolved_at: string | null;
  resolved_by_id: number | null;
  resolution_note: string | null;
  commit_hash: string | null;
  branch_name: string | null;
  repository_url: string | null;
  git_synced: boolean;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskBlockerSummary {
  is_blocked: boolean;
  current_blocker_summary: string | null;
  unresolved_count: number;
}

export interface TaskBase {
  id: number;
  project_id: number;
  column_id: number;
  owner_id: number;
  title: string;
  description: string | null;
  task_type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  labels: string[];
  progress: number;
  is_blocked: boolean;
  current_blocker_summary: string | null;
  acceptance_summary: string | null;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskBoardCard extends TaskBase {
  owner?: UserPublic | null;
  participants: TaskParticipant[];
  subtask_total: number;
  subtask_completed: number;
  latest_work_log_at: string | null;
  blocker_summary?: TaskBlockerSummary | null;
}

export interface TaskDetail extends TaskBase {
  owner?: UserPublic | null;
  column?: BoardColumn | null;
  participants: TaskParticipant[];
  subtasks: Subtask[];
  dependencies: TaskDependency[];
  work_logs: WorkLog[];
  blocker_summary?: TaskBlockerSummary | null;
}

export interface TaskCreatePayload {
  title: string;
  description?: string | null;
  task_type?: TaskType;
  priority?: TaskPriority;
  due_date?: string | null;
  owner_id: number;
  participant_ids?: number[];
  column_id?: number | null;
  status?: TaskStatus;
  labels?: string[];
}

export interface TaskUpdatePayload {
  title?: string;
  description?: string | null;
  task_type?: TaskType;
  priority?: TaskPriority;
  due_date?: string | null;
  owner_id?: number;
  column_id?: number | null;
  labels?: string[];
}

export interface WorkLogCreatePayload {
  work_date: string;
  hours: number;
  content: string;
  work_type?: string;
  is_blocked?: boolean;
  blocked_reason?: string | null;
  commit_hash?: string | null;
  branch_name?: string | null;
  repository_url?: string | null;
}

export interface WorkLogUpdatePayload extends Partial<WorkLogCreatePayload> {}

export interface BlockerResolvePayload {
  resolution_note: string;
}
