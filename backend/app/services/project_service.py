from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.project import BoardColumn, BoardColumnStatus, Project, ProjectMember, ProjectRole
from app.models.team import TeamMember, TeamRole
from app.models.user import User
from app.services.permissions import (
    DomainNotFoundError,
    PermissionDeniedError,
    can_view_team_project,
    ensure_project_manager,
    ensure_team_member,
)

DEFAULT_BOARD_COLUMNS: tuple[tuple[str, str], ...] = (
    ("待办", BoardColumnStatus.TODO.value),
    ("进行中", BoardColumnStatus.IN_PROGRESS.value),
    ("待验收", BoardColumnStatus.IN_REVIEW.value),
    ("打回修改", BoardColumnStatus.REJECTED.value),
    ("已完成", BoardColumnStatus.DONE.value),
)


class DuplicateProjectMemberError(ValueError):
    pass


class InvalidProjectRoleError(ValueError):
    pass


class ProjectDateError(ValueError):
    pass


class LastProjectManagerError(ValueError):
    pass


def _value(payload: Any, name: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        return payload.get(name, default)
    return getattr(payload, name, default)


def _validate_project_role(role: str) -> str:
    if role not in {ProjectRole.PROJECT_MANAGER.value, ProjectRole.PROJECT_MEMBER.value}:
        raise InvalidProjectRoleError("Invalid project role")
    return role


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_project(self, actor: User, team_id: int, payload: Any) -> Project:
        ensure_team_member(self.db, actor, team_id)
        start_date = _value(payload, "start_date")
        end_date = _value(payload, "end_date")
        if start_date and end_date and end_date <= start_date:
            raise ProjectDateError("Project end date must be later than start date")

        project = Project(
            team_id=team_id,
            name=str(_value(payload, "name", "")).strip(),
            description=_value(payload, "description"),
            start_date=start_date,
            end_date=end_date,
            created_by_id=actor.id,
        )
        self.db.add(project)
        self.db.flush()
        self.db.add(ProjectMember(project_id=project.id, user_id=actor.id, role=ProjectRole.PROJECT_MANAGER.value))
        for position, (name, status) in enumerate(DEFAULT_BOARD_COLUMNS, start=1):
            self.db.add(BoardColumn(project_id=project.id, name=name, status=status, position=position))
        self.db.commit()
        self.db.refresh(project)
        return project

    def list_accessible_projects(self, actor: User, team_id: int | None = None) -> list[Project]:
        project_ids = select(ProjectMember.project_id).where(ProjectMember.user_id == actor.id)
        admin_team_ids = select(TeamMember.team_id).where(
            TeamMember.user_id == actor.id,
            TeamMember.role == TeamRole.TEAM_ADMIN.value,
        )
        filters = [or_(Project.id.in_(project_ids), Project.team_id.in_(admin_team_ids))]
        if team_id is not None:
            filters.append(Project.team_id == team_id)
        return list(self.db.scalars(select(Project).where(*filters).order_by(Project.created_at.desc(), Project.id.desc())))

    def get_project_board(self, actor: User, project_id: int) -> Project:
        if not can_view_team_project(self.db, actor, project_id):
            raise PermissionDeniedError("Project access required")
        project = self.db.get(Project, project_id)
        if project is None:
            raise DomainNotFoundError("Project not found")
        return project

    def list_project_members(self, actor: User, project_id: int) -> list[ProjectMember]:
        if not can_view_team_project(self.db, actor, project_id):
            raise PermissionDeniedError("Project access required")
        return list(
            self.db.scalars(
                select(ProjectMember)
                .where(ProjectMember.project_id == project_id)
                .order_by(ProjectMember.created_at, ProjectMember.id)
            )
        )

    def add_project_member(self, actor: User, project_id: int, team_member_user_id: int, role: str) -> ProjectMember:
        ensure_project_manager(self.db, actor, project_id)
        role = _validate_project_role(role)
        project = self._get_project(project_id)
        team_membership = self.db.scalar(
            select(TeamMember).where(TeamMember.team_id == project.team_id, TeamMember.user_id == team_member_user_id)
        )
        if team_membership is None:
            raise PermissionDeniedError("Project member must belong to team")
        existing = self.db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == team_member_user_id,
            )
        )
        if existing is not None:
            raise DuplicateProjectMemberError("Project member already exists")
        member = ProjectMember(project_id=project_id, user_id=team_member_user_id, role=role)
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def update_project_member_role(self, actor: User, project_id: int, user_id: int, role: str) -> ProjectMember:
        ensure_project_manager(self.db, actor, project_id)
        role = _validate_project_role(role)
        member = self._get_project_member(project_id, user_id)
        if member.role == ProjectRole.PROJECT_MANAGER.value and role != ProjectRole.PROJECT_MANAGER.value:
            self._ensure_not_last_manager(project_id, user_id)
        member.role = role
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_project_member(self, actor: User, project_id: int, user_id: int) -> None:
        ensure_project_manager(self.db, actor, project_id)
        member = self._get_project_member(project_id, user_id)
        if member.role == ProjectRole.PROJECT_MANAGER.value:
            self._ensure_not_last_manager(project_id, user_id)
        self.db.delete(member)
        self.db.commit()

    def _get_project(self, project_id: int) -> Project:
        project = self.db.get(Project, project_id)
        if project is None:
            raise DomainNotFoundError("Project not found")
        return project

    def _get_project_member(self, project_id: int, user_id: int) -> ProjectMember:
        member = self.db.scalar(
            select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        )
        if member is None:
            raise DomainNotFoundError("Project member not found")
        return member

    def _ensure_not_last_manager(self, project_id: int, user_id: int) -> None:
        manager_count = (
            self.db.scalar(
                select(func.count()).select_from(ProjectMember).where(
                    ProjectMember.project_id == project_id,
                    ProjectMember.role == ProjectRole.PROJECT_MANAGER.value,
                )
            )
            or 0
        )
        member = self._get_project_member(project_id, user_id)
        if member.role == ProjectRole.PROJECT_MANAGER.value and manager_count <= 1:
            raise LastProjectManagerError("Project must retain at least one manager")
