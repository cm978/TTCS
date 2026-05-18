from datetime import date

import pytest

from app.models.project import ProjectMember, ProjectRole
from app.models.task import TaskParticipant, TaskPriority, TaskStatus, TaskType, WorkLog
from app.schemas.task import BlockerResolveRequest, WorkLogCreateRequest
from app.models.team import TeamMember, TeamRole
from app.services.permissions import PermissionDeniedError, ensure_task_owner_or_project_manager
from app.services.project_service import ProjectService
from app.services.task_service import (
    TaskDependencyCycleError,
    TaskParticipantLimitError,
    TaskService,
)
from app.services.task_state import InvalidTaskStatusTransitionError
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


def test_work_log_schema_validates_hours_blocker_notes_and_code_fields():
    valid = WorkLogCreateRequest(
        work_date=date.today(),
        hours=1.5,
        content="Implemented task service",
        is_blocked=True,
        blocked_reason="Blocked by missing fixture",
        commit_hash="abc123",
        branch_name="feature/task-domain",
        repository_url="https://example.com/repo",
    )

    assert valid.commit_hash == "abc123"
    assert WorkLog.__tablename__ == "work_logs"

    with pytest.raises(ValueError):
        WorkLogCreateRequest(work_date=date.today(), hours=0.25, content="Too small")

    with pytest.raises(ValueError):
        WorkLogCreateRequest(work_date=date.today(), hours=1, content="Blocked", is_blocked=True, blocked_reason="short")

    with pytest.raises(ValueError):
        BlockerResolveRequest(resolution_note="too short")


def test_team_admin_without_project_role_cannot_manage_task_permissions(db_session):
    owner = make_user(db_session, "owner@example.com")
    admin = make_user(db_session, "admin@example.com")
    team_service = TeamService(db_session)
    team = team_service.create_team(owner, payload(name="Demo Team", description=None))
    invitation = team_service.invite_member(owner, team.id, payload(email=admin.email, role=TeamRole.TEAM_ADMIN.value))
    team_service.accept_invitation(admin, invitation.id)
    project = ProjectService(db_session).create_project(owner, team.id, payload(name="Launch", description=None))
    task = TaskService(db_session).create_task(
        owner,
        project.id,
        payload(title="Implement task model", owner_id=owner.id, participant_ids=[]),
    )

    with pytest.raises(PermissionDeniedError):
        ensure_task_owner_or_project_manager(db_session, admin, task.id)

    with pytest.raises(PermissionDeniedError):
        TaskService(db_session).update_task(admin, task.id, payload(title="Blocked mutation"))


def add_project_member_direct(db_session, project, user, role=ProjectRole.PROJECT_MEMBER.value):
    db_session.add(TeamMember(team_id=project.team_id, user_id=user.id, role=TeamRole.TEAM_MEMBER.value))
    db_session.add(ProjectMember(project_id=project.id, user_id=user.id, role=role))
    db_session.commit()


def make_project(db_session):
    owner = make_user(db_session, "owner-task@example.com")
    project = ProjectService(db_session).create_project(
        owner,
        TeamService(db_session).create_team(owner, payload(name="Task Team", description=None)).id,
        payload(name="Launch", description=None),
    )
    return owner, project


def test_create_task_auto_adds_owner_and_counts_participant_limit(db_session):
    owner, project = make_project(db_session)
    members = [make_user(db_session, f"member-{index}@example.com") for index in range(1, 6)]
    for member in members:
        add_project_member_direct(db_session, project, member)

    task = TaskService(db_session).create_task(
        owner,
        project.id,
        payload(
            title="Implement execution board",
            owner_id=owner.id,
            participant_ids=[member.id for member in members[:4]],
            task_type=TaskType.CODE.value,
            priority=TaskPriority.HIGH.value,
        ),
    )
    participants = db_session.query(TaskParticipant).filter_by(task_id=task.id, removed_at=None).all()

    assert task.status == TaskStatus.TODO.value
    assert task.column_id == project.columns[0].id
    assert {participant.user_id for participant in participants} == {owner.id, *(member.id for member in members[:4])}

    with pytest.raises(TaskParticipantLimitError):
        TaskService(db_session).create_task(
            owner,
            project.id,
            payload(title="Too many", owner_id=owner.id, participant_ids=[member.id for member in members]),
        )


def test_task_can_have_owner_as_sole_participant(db_session):
    owner, project = make_project(db_session)

    task = TaskService(db_session).create_task(
        owner,
        project.id,
        payload(title="Owner-only task", owner_id=owner.id, participant_ids=[]),
    )
    participants = db_session.query(TaskParticipant).filter_by(task_id=task.id, removed_at=None).all()

    assert len(participants) == 1
    assert participants[0].user_id == owner.id


def test_owner_and_project_manager_manage_participants_but_ordinary_participant_cannot(db_session):
    owner, project = make_project(db_session)
    participant = make_user(db_session, "participant@example.com")
    extra = make_user(db_session, "extra@example.com")
    manager = make_user(db_session, "manager@example.com")
    add_project_member_direct(db_session, project, participant)
    add_project_member_direct(db_session, project, extra)
    add_project_member_direct(db_session, project, manager, ProjectRole.PROJECT_MANAGER.value)
    service = TaskService(db_session)
    task = service.create_task(
        owner,
        project.id,
        payload(title="Participant rules", owner_id=owner.id, participant_ids=[participant.id]),
    )

    with pytest.raises(PermissionDeniedError):
        service.add_participant(participant, task.id, extra.id)

    added = service.add_participant(manager, task.id, extra.id)
    removed = service.remove_participant(owner, task.id, participant.id)

    assert added.user_id == extra.id
    assert removed.removed_at is not None
    assert db_session.query(TaskParticipant).filter_by(task_id=task.id, user_id=participant.id).one()


def test_soft_delete_requires_project_manager(db_session):
    owner, project = make_project(db_session)
    participant = make_user(db_session, "delete-participant@example.com")
    add_project_member_direct(db_session, project, participant)
    task = TaskService(db_session).create_task(
        owner,
        project.id,
        payload(title="Delete guarded", owner_id=participant.id, participant_ids=[]),
    )

    with pytest.raises(PermissionDeniedError):
        TaskService(db_session).soft_delete_task(participant, task.id)

    deleted = TaskService(db_session).soft_delete_task(owner, task.id)
    assert deleted.deleted_at is not None
    assert deleted.status == TaskStatus.DELETED.value


def test_subtasks_drive_progress_without_status_pseudo_progress(db_session):
    owner, project = make_project(db_session)
    service = TaskService(db_session)
    task = service.create_task(owner, project.id, payload(title="Progress rules", owner_id=owner.id, participant_ids=[]))

    service.change_status(owner, task.id, TaskStatus.IN_PROGRESS.value)
    assert service.recalculate_progress(task.id) == 0

    first = service.create_subtask(owner, task.id, payload(title="Draft model"))
    service.create_subtask(owner, task.id, payload(title="Write tests"))
    service.update_subtask(owner, first.id, payload(is_completed=True))

    db_session.refresh(task)
    assert task.progress == 50


def test_dependency_cycle_and_done_transition_are_rejected(db_session):
    owner, project = make_project(db_session)
    service = TaskService(db_session)
    first = service.create_task(owner, project.id, payload(title="First task", owner_id=owner.id, participant_ids=[]))
    second = service.create_task(owner, project.id, payload(title="Second task", owner_id=owner.id, participant_ids=[]))

    service.add_dependency(owner, first.id, second.id)

    with pytest.raises(TaskDependencyCycleError):
        service.add_dependency(owner, second.id, first.id)

    service.change_status(owner, first.id, TaskStatus.IN_PROGRESS.value)
    with pytest.raises(InvalidTaskStatusTransitionError):
        service.change_status(owner, first.id, TaskStatus.DONE.value)
