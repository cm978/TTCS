from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectMember, ProjectRole
from app.models.team import Team, TeamInvitation, TeamInvitationStatus, TeamMember, TeamRole
from app.models.user import User
from app.services.permissions import DomainNotFoundError, PermissionDeniedError, ensure_team_admin, ensure_team_member


class DuplicateTeamError(ValueError):
    pass


class TeamLimitExceededError(ValueError):
    pass


class DuplicateInvitationError(ValueError):
    pass


class InvalidRoleError(ValueError):
    pass


class InvitationUnavailableError(ValueError):
    pass


class LastTeamAdminError(ValueError):
    pass


class LastProjectManagerInTeamError(ValueError):
    pass


def _value(payload: Any, name: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        return payload.get(name, default)
    return getattr(payload, name, default)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _validate_team_role(role: str) -> str:
    if role not in {TeamRole.TEAM_ADMIN.value, TeamRole.TEAM_MEMBER.value}:
        raise InvalidRoleError("Invalid team role")
    return role


class TeamService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_team(self, actor: User, payload: Any) -> Team:
        name = str(_value(payload, "name", "")).strip()
        description = _value(payload, "description")
        if self.db.scalar(select(Team).where(Team.name == name)) is not None:
            raise DuplicateTeamError("Team name already exists")
        created_count = self.db.scalar(select(func.count()).select_from(Team).where(Team.created_by_id == actor.id)) or 0
        if created_count >= 5:
            raise TeamLimitExceededError("Team creation limit exceeded")

        team = Team(name=name, description=description, created_by_id=actor.id)
        self.db.add(team)
        self.db.flush()
        self.db.add(TeamMember(team_id=team.id, user_id=actor.id, role=TeamRole.TEAM_ADMIN.value))
        self.db.commit()
        self.db.refresh(team)
        return team

    def get_team_for_user(self, actor: User, team_id: int) -> Team:
        ensure_team_member(self.db, actor, team_id)
        team = self.db.get(Team, team_id)
        if team is None:
            raise DomainNotFoundError("Team not found")
        return team

    def list_my_teams(self, actor: User) -> list[Team]:
        return list(
            self.db.scalars(
                select(Team)
                .join(TeamMember, TeamMember.team_id == Team.id)
                .where(TeamMember.user_id == actor.id)
                .order_by(Team.created_at.desc(), Team.id.desc())
            )
        )

    def list_team_members(self, actor: User, team_id: int) -> list[TeamMember]:
        ensure_team_member(self.db, actor, team_id)
        return list(
            self.db.scalars(
                select(TeamMember).where(TeamMember.team_id == team_id).order_by(TeamMember.created_at, TeamMember.id)
            )
        )

    def invite_member(self, actor: User, team_id: int, payload: Any) -> TeamInvitation:
        ensure_team_admin(self.db, actor, team_id)
        email = _normalize_email(str(_value(payload, "email", "")))
        role = _validate_team_role(str(_value(payload, "role", TeamRole.TEAM_MEMBER.value)))
        self._expire_pending_invitations(team_id=team_id, email=email)

        duplicate = self.db.scalar(
            select(TeamInvitation).where(
                TeamInvitation.team_id == team_id,
                TeamInvitation.email == email,
                TeamInvitation.status == TeamInvitationStatus.PENDING.value,
            )
        )
        if duplicate is not None:
            raise DuplicateInvitationError("Pending invitation already exists")

        invitation = TeamInvitation(
            team_id=team_id,
            email=email,
            role=role,
            status=TeamInvitationStatus.PENDING.value,
            invited_by_id=actor.id,
            expires_at=_now() + timedelta(days=7),
        )
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        return invitation

    def list_team_invitations(self, actor: User, team_id: int) -> list[TeamInvitation]:
        ensure_team_admin(self.db, actor, team_id)
        self._expire_pending_invitations(team_id=team_id)
        self.db.commit()
        return list(
            self.db.scalars(
                select(TeamInvitation)
                .where(TeamInvitation.team_id == team_id)
                .order_by(TeamInvitation.created_at.desc(), TeamInvitation.id.desc())
            )
        )

    def list_my_invitations(self, actor: User) -> list[TeamInvitation]:
        email = _normalize_email(actor.email)
        self._expire_pending_invitations(email=email)
        self.db.commit()
        return list(
            self.db.scalars(
                select(TeamInvitation)
                .where(TeamInvitation.email == email, TeamInvitation.status == TeamInvitationStatus.PENDING.value)
                .order_by(TeamInvitation.created_at.desc(), TeamInvitation.id.desc())
            )
        )

    def accept_invitation(self, actor: User, invitation_id: int) -> TeamInvitation:
        invitation = self.db.get(TeamInvitation, invitation_id)
        if invitation is None:
            raise DomainNotFoundError("Invitation not found")
        if invitation.email != _normalize_email(actor.email):
            raise PermissionDeniedError("Invitation email does not match current user")
        if invitation.status != TeamInvitationStatus.PENDING.value:
            raise InvitationUnavailableError("Invitation is not pending")
        if _normalize_datetime(invitation.expires_at) < _now():
            invitation.status = TeamInvitationStatus.EXPIRED.value
            self.db.commit()
            raise InvitationUnavailableError("Invitation expired")

        existing = self.db.scalar(
            select(TeamMember).where(TeamMember.team_id == invitation.team_id, TeamMember.user_id == actor.id)
        )
        if existing is None:
            self.db.add(TeamMember(team_id=invitation.team_id, user_id=actor.id, role=invitation.role))
        invitation.status = TeamInvitationStatus.ACCEPTED.value
        invitation.accepted_by_id = actor.id
        invitation.accepted_at = _now()
        self.db.commit()
        self.db.refresh(invitation)
        return invitation

    def cancel_invitation(self, actor: User, invitation_id: int) -> TeamInvitation:
        invitation = self.db.get(TeamInvitation, invitation_id)
        if invitation is None:
            raise DomainNotFoundError("Invitation not found")
        ensure_team_admin(self.db, actor, invitation.team_id)
        if invitation.status != TeamInvitationStatus.PENDING.value:
            raise InvitationUnavailableError("Invitation is not pending")
        invitation.status = TeamInvitationStatus.CANCELLED.value
        invitation.cancelled_at = _now()
        self.db.commit()
        self.db.refresh(invitation)
        return invitation

    def update_member_role(self, actor: User, team_id: int, user_id: int, role: str) -> TeamMember:
        ensure_team_admin(self.db, actor, team_id)
        role = _validate_team_role(role)
        member = self._get_member(team_id, user_id)
        if member.role == TeamRole.TEAM_ADMIN.value and role != TeamRole.TEAM_ADMIN.value:
            self._ensure_not_last_admin(team_id, user_id)
        member.role = role
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_member(self, actor: User, team_id: int, user_id: int) -> None:
        ensure_team_admin(self.db, actor, team_id)
        member = self._get_member(team_id, user_id)
        if member.role == TeamRole.TEAM_ADMIN.value:
            self._ensure_not_last_admin(team_id, user_id)

        project_ids = select(Project.id).where(Project.team_id == team_id)
        project_memberships = list(
            self.db.scalars(
                select(ProjectMember).where(ProjectMember.user_id == user_id, ProjectMember.project_id.in_(project_ids))
            )
        )
        for project_member in project_memberships:
            if project_member.role == ProjectRole.PROJECT_MANAGER.value:
                manager_count = (
                    self.db.scalar(
                        select(func.count()).select_from(ProjectMember).where(
                            ProjectMember.project_id == project_member.project_id,
                            ProjectMember.role == ProjectRole.PROJECT_MANAGER.value,
                        )
                    )
                    or 0
                )
                if manager_count <= 1:
                    raise LastProjectManagerInTeamError("Project must retain at least one manager")

        for project_member in project_memberships:
            self.db.delete(project_member)
        self.db.delete(member)
        self.db.commit()

    def _get_member(self, team_id: int, user_id: int) -> TeamMember:
        member = self.db.scalar(select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id))
        if member is None:
            raise DomainNotFoundError("Team member not found")
        return member

    def _ensure_not_last_admin(self, team_id: int, user_id: int) -> None:
        admin_count = (
            self.db.scalar(
                select(func.count()).select_from(TeamMember).where(
                    TeamMember.team_id == team_id,
                    TeamMember.role == TeamRole.TEAM_ADMIN.value,
                )
            )
            or 0
        )
        member = self._get_member(team_id, user_id)
        if member.role == TeamRole.TEAM_ADMIN.value and admin_count <= 1:
            raise LastTeamAdminError("Team must retain at least one administrator")

    def _expire_pending_invitations(self, team_id: int | None = None, email: str | None = None) -> None:
        filters = [TeamInvitation.status == TeamInvitationStatus.PENDING.value]
        if team_id is not None:
            filters.append(TeamInvitation.team_id == team_id)
        if email is not None:
            filters.append(TeamInvitation.email == email)
        for invitation in self.db.scalars(select(TeamInvitation).where(*filters)):
            if _normalize_datetime(invitation.expires_at) < _now():
                invitation.status = TeamInvitationStatus.EXPIRED.value
