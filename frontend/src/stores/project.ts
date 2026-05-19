import { defineStore } from "pinia";

import {
  addProjectMember,
  createProject,
  getProject,
  getProjectBoard,
  listProjectMembers,
  listProjects,
  removeProjectMember,
  updateProjectMemberRole
} from "../api/projects";
import type {
  Project,
  ProjectBoard,
  ProjectCreatePayload,
  ProjectMember,
  ProjectMemberAddPayload,
  ProjectMemberRoleUpdatePayload
} from "../types/project";

interface ProjectState {
  projects: Project[];
  activeProject: Project | null;
  activeBoard: ProjectBoard | null;
  membersByProject: Record<number, ProjectMember[]>;
  loading: boolean;
  error: string | null;
}

function projectError(fallback: string): string {
  return fallback;
}

export const useProjectStore = defineStore("project", {
  state: (): ProjectState => ({
    projects: [],
    activeProject: null,
    activeBoard: null,
    membersByProject: {},
    loading: false,
    error: null
  }),
  actions: {
    clearError() {
      this.error = null;
    },
    async loadProjects(teamId?: number) {
      this.loading = true;
      this.error = null;
      try {
        this.projects = await listProjects(teamId);
        return this.projects;
      } catch {
        this.error = projectError("项目加载失败。请稍后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async createProject(teamId: number, payload: ProjectCreatePayload) {
      this.loading = true;
      this.error = null;
      try {
        const project = await createProject(teamId, payload);
        this.projects = [project, ...this.projects.filter((item) => item.id !== project.id)];
        return project;
      } catch {
        this.error = projectError("创建项目失败。请检查项目信息后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async loadBoard(projectId: number) {
      this.loading = true;
      this.error = null;
      try {
        this.activeBoard = await getProjectBoard(projectId);
        this.activeProject = this.activeBoard.project;
        this.membersByProject[projectId] = this.activeBoard.members;
        return this.activeBoard;
      } catch {
        this.error = projectError("项目看板加载失败。请稍后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async loadProject(projectId: number) {
      this.loading = true;
      this.error = null;
      try {
        const project = await getProject(projectId);
        this.activeProject = project;
        this.projects = [project, ...this.projects.filter((item) => item.id !== project.id)];
        return project;
      } catch {
        this.error = projectError("项目详情加载失败。请稍后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async loadProjectMembers(projectId: number) {
      this.membersByProject[projectId] = await listProjectMembers(projectId);
      return this.membersByProject[projectId];
    },
    async addMember(projectId: number, payload: ProjectMemberAddPayload) {
      const member = await addProjectMember(projectId, payload);
      this.membersByProject[projectId] = [member, ...(this.membersByProject[projectId] ?? [])];
      return member;
    },
    async updateMemberRole(projectId: number, userId: number, payload: ProjectMemberRoleUpdatePayload) {
      const member = await updateProjectMemberRole(projectId, userId, payload);
      const members = this.membersByProject[projectId] ?? [];
      this.membersByProject[projectId] = members.map((item) => (item.user.id === userId ? member : item));
      return member;
    },
    async removeMember(projectId: number, userId: number) {
      await removeProjectMember(projectId, userId);
      this.membersByProject[projectId] = (this.membersByProject[projectId] ?? []).filter(
        (member) => member.user.id !== userId
      );
    }
  }
});
