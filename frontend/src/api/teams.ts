import { apiClient } from "./client";
import type {
  Team,
  TeamCreatePayload,
  TeamInvitation,
  TeamInvitationCreatePayload,
  TeamMember,
  TeamMemberRoleUpdatePayload
} from "../types/team";

export async function createTeam(payload: TeamCreatePayload): Promise<Team> {
  const { data } = await apiClient.post<Team>("/teams", payload);
  return data;
}

export async function listTeams(): Promise<Team[]> {
  const { data } = await apiClient.get<Team[]>("/teams");
  return data;
}

export async function getTeam(teamId: number): Promise<Team> {
  const { data } = await apiClient.get<Team>(`/teams/${teamId}`);
  return data;
}

export async function listTeamMembers(teamId: number): Promise<TeamMember[]> {
  const { data } = await apiClient.get<TeamMember[]>(`/teams/${teamId}/members`);
  return data;
}

export async function updateTeamMemberRole(
  teamId: number,
  userId: number,
  payload: TeamMemberRoleUpdatePayload
): Promise<TeamMember> {
  const { data } = await apiClient.patch<TeamMember>(`/teams/${teamId}/members/${userId}`, payload);
  return data;
}

export async function removeTeamMember(teamId: number, userId: number): Promise<void> {
  await apiClient.delete(`/teams/${teamId}/members/${userId}`);
}

export async function inviteTeamMember(teamId: number, payload: TeamInvitationCreatePayload): Promise<TeamInvitation> {
  const { data } = await apiClient.post<TeamInvitation>(`/teams/${teamId}/invitations`, payload);
  return data;
}

export async function listTeamInvitations(teamId: number): Promise<TeamInvitation[]> {
  const { data } = await apiClient.get<TeamInvitation[]>(`/teams/${teamId}/invitations`);
  return data;
}

export async function listMyInvitations(): Promise<TeamInvitation[]> {
  const { data } = await apiClient.get<TeamInvitation[]>("/teams/my-invitations");
  return data;
}

export async function acceptInvitation(invitationId: number): Promise<TeamInvitation> {
  const { data } = await apiClient.post<TeamInvitation>(`/teams/invitations/${invitationId}/accept`);
  return data;
}

export async function cancelInvitation(invitationId: number): Promise<TeamInvitation> {
  const { data } = await apiClient.post<TeamInvitation>(`/teams/invitations/${invitationId}/cancel`);
  return data;
}
