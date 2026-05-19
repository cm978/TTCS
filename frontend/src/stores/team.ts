import { defineStore } from "pinia";

import {
  acceptInvitation,
  cancelInvitation,
  createTeam,
  getTeam,
  inviteTeamMember,
  listMyInvitations,
  listTeamInvitations,
  listTeamMembers,
  listTeams,
  removeTeamMember,
  updateTeamMemberRole
} from "../api/teams";
import type {
  Team,
  TeamCreatePayload,
  TeamInvitation,
  TeamInvitationCreatePayload,
  TeamMember,
  TeamMemberRoleUpdatePayload
} from "../types/team";

interface TeamState {
  teams: Team[];
  activeTeam: Team | null;
  selectedTeamId: number | null;
  membersByTeam: Record<number, TeamMember[]>;
  invitationsByTeam: Record<number, TeamInvitation[]>;
  myInvitations: TeamInvitation[];
  loading: boolean;
  error: string | null;
}

function teamError(fallback: string): string {
  return fallback;
}

export const useTeamStore = defineStore("team", {
  state: (): TeamState => ({
    teams: [],
    activeTeam: null,
    selectedTeamId: null,
    membersByTeam: {},
    invitationsByTeam: {},
    myInvitations: [],
    loading: false,
    error: null
  }),
  getters: {
    selectedTeam: (state) => state.teams.find((team) => team.id === state.selectedTeamId) ?? null,
    hasTeams: (state) => state.teams.length > 0
  },
  actions: {
    clearError() {
      this.error = null;
    },
    async loadAppData() {
      this.loading = true;
      this.error = null;
      try {
        const [teams, invitations] = await Promise.all([listTeams(), listMyInvitations()]);
        this.teams = teams;
        this.myInvitations = invitations;
        if (!this.selectedTeamId && teams.length > 0) {
          this.selectedTeamId = teams[0].id;
        }
      } catch {
        this.error = teamError("团队与邀请加载失败。请稍后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async createTeam(payload: TeamCreatePayload) {
      this.loading = true;
      this.error = null;
      try {
        const team = await createTeam(payload);
        this.teams = [team, ...this.teams.filter((item) => item.id !== team.id)];
        this.selectedTeamId = team.id;
        return team;
      } catch {
        this.error = teamError("创建团队失败。请检查团队名称后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async loadTeam(teamId: number) {
      this.loading = true;
      this.error = null;
      try {
        const team = await getTeam(teamId);
        this.activeTeam = team;
        this.selectedTeamId = team.id;
        this.teams = [team, ...this.teams.filter((item) => item.id !== team.id)];
        return team;
      } catch {
        this.error = teamError("团队详情加载失败。请稍后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async loadTeamMembers(teamId: number) {
      this.membersByTeam[teamId] = await listTeamMembers(teamId);
      return this.membersByTeam[teamId];
    },
    async loadTeamInvitations(teamId: number) {
      this.invitationsByTeam[teamId] = await listTeamInvitations(teamId);
      return this.invitationsByTeam[teamId];
    },
    async inviteMember(teamId: number, payload: TeamInvitationCreatePayload) {
      const invitation = await inviteTeamMember(teamId, payload);
      this.invitationsByTeam[teamId] = [invitation, ...(this.invitationsByTeam[teamId] ?? [])];
      return invitation;
    },
    async acceptInvitation(invitationId: number) {
      const invitation = await acceptInvitation(invitationId);
      this.myInvitations = this.myInvitations.filter((item) => item.id !== invitationId);
      await this.loadAppData();
      return invitation;
    },
    async cancelInvitation(invitationId: number) {
      const invitation = await cancelInvitation(invitationId);
      const teamInvitations = this.invitationsByTeam[invitation.team_id] ?? [];
      this.invitationsByTeam[invitation.team_id] = teamInvitations.map((item) =>
        item.id === invitation.id ? invitation : item
      );
      return invitation;
    },
    async updateMemberRole(teamId: number, userId: number, payload: TeamMemberRoleUpdatePayload) {
      const member = await updateTeamMemberRole(teamId, userId, payload);
      const members = this.membersByTeam[teamId] ?? [];
      this.membersByTeam[teamId] = members.map((item) => (item.user.id === userId ? member : item));
      return member;
    },
    async removeMember(teamId: number, userId: number) {
      await removeTeamMember(teamId, userId);
      this.membersByTeam[teamId] = (this.membersByTeam[teamId] ?? []).filter((member) => member.user.id !== userId);
    }
  }
});
