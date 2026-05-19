import { apiClient } from "./client";
import type {
  Project,
  ProjectBoard,
  ProjectCreatePayload,
  ProjectMember,
  ProjectMemberAddPayload,
  ProjectMemberRoleUpdatePayload
} from "../types/project";

export async function createProject(teamId: number, payload: ProjectCreatePayload): Promise<Project> {
  const { data } = await apiClient.post<Project>(`/teams/${teamId}/projects`, payload);
  return data;
}

export async function listProjects(teamId?: number): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/projects", { params: teamId ? { team_id: teamId } : undefined });
  return data;
}

export async function getProject(projectId: number): Promise<Project> {
  const { data } = await apiClient.get<ProjectBoard>(`/projects/${projectId}/board`);
  return data.project;
}

export async function getProjectBoard(projectId: number): Promise<ProjectBoard> {
  const { data } = await apiClient.get<ProjectBoard>(`/projects/${projectId}/board`);
  return data;
}

export async function listProjectMembers(projectId: number): Promise<ProjectMember[]> {
  const { data } = await apiClient.get<ProjectMember[]>(`/projects/${projectId}/members`);
  return data;
}

export async function addProjectMember(projectId: number, payload: ProjectMemberAddPayload): Promise<ProjectMember> {
  const { data } = await apiClient.post<ProjectMember>(`/projects/${projectId}/members`, payload);
  return data;
}

export async function updateProjectMemberRole(
  projectId: number,
  userId: number,
  payload: ProjectMemberRoleUpdatePayload
): Promise<ProjectMember> {
  const { data } = await apiClient.patch<ProjectMember>(`/projects/${projectId}/members/${userId}`, payload);
  return data;
}

export async function removeProjectMember(projectId: number, userId: number): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/members/${userId}`);
}
