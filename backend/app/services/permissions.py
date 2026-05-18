from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectMember, ProjectRole
from app.models.task import Task, TaskParticipant
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


def ensure_task_visible(db: Session, actor: User, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.deleted_at is not None:
        raise DomainNotFoundError("Task not found")
    if not can_view_team_project(db, actor, task.project_id):
        raise PermissionDeniedError("Task access required")
    return task


def _active_task_participant(db: Session, actor: User, task_id: int) -> TaskParticipant | None:
    return db.scalar(
        select(TaskParticipant).where(
            TaskParticipant.task_id == task_id,
            TaskParticipant.user_id == actor.id,
            TaskParticipant.removed_at.is_(None),
        )
    )


def _project_manager_membership(db: Session, actor: User, project_id: int) -> ProjectMember | None:
    return db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == actor.id,
            ProjectMember.role == ProjectRole.PROJECT_MANAGER.value,
        )
    )


def ensure_task_owner_or_project_manager(db: Session, actor: User, task_id: int) -> Task:
    task = ensure_task_visible(db, actor, task_id)
    if task.owner_id == actor.id:
        return task
    if _project_manager_membership(db, actor, task.project_id) is not None:
        return task
    raise PermissionDeniedError("Task Owner or project manager required")


def ensure_task_participant_or_owner(db: Session, actor: User, task_id: int) -> Task:
    task = ensure_task_visible(db, actor, task_id)
    if task.owner_id == actor.id:
        return task
    if _active_task_participant(db, actor, task_id) is not None:
        return task
    if _project_manager_membership(db, actor, task.project_id) is not None:
        return task
    raise PermissionDeniedError("Task participant required")


def can_manage_task_participants(db: Session, actor: User, task: Task) -> bool:
    if task.owner_id == actor.id:
        return True
    return _project_manager_membership(db, actor, task.project_id) is not None
