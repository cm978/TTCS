import type { UserPublic } from "./auth";

export type TeamRole = "TEAM_ADMIN" | "TEAM_MEMBER";
export type TeamInvitationStatus = "PENDING" | "ACCEPTED" | "EXPIRED" | "CANCELLED";

export interface Team {
  id: number;
  name: string;
  description: string | null;
  created_by_id: number;
  created_at: string;
}

export interface TeamMember {
  id: number;
  team_id: number;
  user: UserPublic;
  role: TeamRole;
  created_at: string;
}

export interface TeamInvitation {
  id: number;
  team_id: number;
  email: string;
  role: TeamRole;
  status: TeamInvitationStatus;
  invited_by_id: number;
  accepted_by_id: number | null;
  expires_at: string;
  accepted_at: string | null;
  cancelled_at: string | null;
  created_at: string;
}

export interface TeamCreatePayload {
  name: string;
  description?: string | null;
}

export interface TeamInvitationCreatePayload {
  email: string;
  role: TeamRole;
}

export interface TeamMemberRoleUpdatePayload {
  role: TeamRole;
}
