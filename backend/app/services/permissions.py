from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectMember, ProjectRole
from app.models.team import TeamMember, TeamRole
from app.models.user import User


class DomainNotFoundError(ValueError):
    pass


class PermissionDeniedError(ValueError):
    pass


def ensure_team_member(db: Session, actor: User, team_id: int) -> TeamMember:
    membership = db.scalar(select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == actor.id))
    if membership is None:
        raise PermissionDeniedError("Team membership required")
    return membership


def ensure_team_admin(db: Session, actor: User, team_id: int) -> TeamMember:
    membership = ensure_team_member(db, actor, team_id)
    if membership.role != TeamRole.TEAM_ADMIN.value:
        raise PermissionDeniedError("Team administrator required")
    return membership


def ensure_project_member(db: Session, actor: User, project_id: int) -> ProjectMember:
    membership = db.scalar(
        select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == actor.id)
    )
    if membership is None:
        raise PermissionDeniedError("Project membership required")
    return membership


def ensure_project_manager(db: Session, actor: User, project_id: int) -> ProjectMember:
    membership = ensure_project_member(db, actor, project_id)
    if membership.role != ProjectRole.PROJECT_MANAGER.value:
        raise PermissionDeniedError("Project manager required")
    return membership


def can_view_team_project(db: Session, actor: User, project_id: int) -> bool:
    project = db.get(Project, project_id)
    if project is None:
        raise DomainNotFoundError("Project not found")

    project_membership = db.scalar(
        select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == actor.id)
    )
    if project_membership is not None:
        return True

    team_membership = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == project.team_id,
            TeamMember.user_id == actor.id,
            TeamMember.role == TeamRole.TEAM_ADMIN.value,
        )
    )
    return team_membership is not None
