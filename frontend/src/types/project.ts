import type { UserPublic } from "./auth";

export type ProjectRole = "PROJECT_MANAGER" | "PROJECT_MEMBER";
export type BoardColumnStatus = "TODO" | "IN_PROGRESS" | "IN_REVIEW" | "REJECTED" | "DONE";

export interface Project {
  id: number;
  team_id: number;
  name: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  created_by_id: number;
  created_at: string;
}

export interface ProjectMember {
  id: number;
  project_id: number;
  user: UserPublic;
  role: ProjectRole;
  created_at: string;
}

export interface BoardColumn {
  id: number;
  project_id: number;
  name: string;
  status: BoardColumnStatus;
  position: number;
}

export interface ProjectBoard {
  project: Project;
  members: ProjectMember[];
  columns: BoardColumn[];
}

export interface ProjectCreatePayload {
  name: string;
  description?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ProjectMemberAddPayload {
  user_id: number;
  role: ProjectRole;
}

export interface ProjectMemberRoleUpdatePayload {
  role: ProjectRole;
}
