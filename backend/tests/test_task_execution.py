import pytest

from app.models.task import TaskPriority, TaskStatus, TaskType
from app.models.team import TeamRole
from app.services.permissions import PermissionDeniedError, ensure_task_owner_or_project_manager
from app.services.project_service import ProjectService
from app.services.team_service import TeamService
from tests.test_team_project import make_user, payload


def test_task_domain_enums_match_phase3_contract():
    assert [status.value for status in TaskStatus] == [
        "TODO",
        "IN_PROGRESS",
        "IN_REVIEW",
        "REJECTED",
        "DONE",
        "CLOSED",
        "DELETED",
    ]
    assert [task_type.value for task_type in TaskType] == ["GENERAL", "DOCUMENT", "CODE"]
    assert [priority.value for priority in TaskPriority] == ["URGENT", "HIGH", "MEDIUM", "LOW"]


def test_team_admin_without_project_role_cannot_manage_task_permissions(db_session):
    owner = make_user(db_session, "owner@example.com")
    admin = make_user(db_session, "admin@example.com")
    team_service = TeamService(db_session)
    team = team_service.create_team(owner, payload(name="Demo Team", description=None))
    invitation = team_service.invite_member(owner, team.id, payload(email=admin.email, role=TeamRole.TEAM_ADMIN.value))
    team_service.accept_invitation(admin, invitation.id)
    project = ProjectService(db_session).create_project(owner, team.id, payload(name="Launch", description=None))

    from app.models.task import Task

    task = Task(
        project_id=project.id,
        column_id=project.columns[0].id,
        owner_id=owner.id,
        title="Implement task model",
        task_type=TaskType.GENERAL.value,
        status=TaskStatus.TODO.value,
        priority=TaskPriority.MEDIUM.value,
        labels=[],
    )
    db_session.add(task)
    db_session.commit()

    with pytest.raises(PermissionDeniedError):
        ensure_task_owner_or_project_manager(db_session, admin, task.id)
