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
from app.services.work_log_service import WorkLogService, WorkLogValidationError
from tests.test_team_project import auth_headers, current_user_id, make_user, payload


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


def test_work_log_blockers_recompute_task_blocked_state_and_latest_summary(db_session):
    owner, project = make_project(db_session)
    service = TaskService(db_session)
    task = service.create_task(owner, project.id, payload(title="Blocked task", owner_id=owner.id, participant_ids=[]))
    logs = WorkLogService(db_session)

    first = logs.create_work_log(
        owner,
        task.id,
        payload(
            work_date=date.today(),
            hours=1,
            content="Found dependency issue",
            is_blocked=True,
            blocked_reason="Waiting for API contract",
        ),
    )
    second = logs.create_work_log(
        owner,
        task.id,
        payload(
            work_date=date.today(),
            hours=0.5,
            content="Second blocker",
            is_blocked=True,
            blocked_reason="Waiting for test account",
        ),
    )

    db_session.refresh(task)
    assert task.is_blocked is True
    assert task.current_blocker_summary == "Waiting for test account"
    assert logs.can_submit_acceptance_preview(task.id) is False

    logs.resolve_blocker(owner, second.id, payload(resolution_note="Test account created"))
    db_session.refresh(task)
    assert task.is_blocked is True
    assert task.current_blocker_summary == "Waiting for API contract"

    logs.resolve_blocker(owner, first.id, payload(resolution_note="API contract confirmed"))
    db_session.refresh(task)
    assert task.is_blocked is False
    assert task.current_blocker_summary is None


def test_work_log_rejects_future_dates_and_soft_delete_preserves_row(db_session):
    owner, project = make_project(db_session)
    task = TaskService(db_session).create_task(
        owner,
        project.id,
        payload(title="Work log audit", owner_id=owner.id, participant_ids=[]),
    )
    logs = WorkLogService(db_session)

    with pytest.raises(WorkLogValidationError):
        logs.create_work_log(
            owner,
            task.id,
            payload(work_date=date(2999, 1, 1), hours=1, content="From the future"),
        )

    work_log = logs.create_work_log(
        owner,
        task.id,
        payload(work_date=date.today(), hours=2, content="Implemented persistence", commit_hash="abc123"),
    )
    deleted = logs.soft_delete_work_log(owner, work_log.id)

    assert deleted.deleted_at is not None
    assert logs.list_task_logs(owner, task.id) == []
    assert logs.list_task_logs(owner, task.id, include_deleted=True)[0].id == work_log.id


def create_api_project(client):
    owner_headers = auth_headers(client, "api-owner@example.com", "Owner")
    owner_id = current_user_id(client, owner_headers)
    team_id = client.post("/api/v1/teams", json={"name": "API Team"}, headers=owner_headers).json()["id"]
    project_id = client.post(
        f"/api/v1/teams/{team_id}/projects",
        json={"name": "API Launch"},
        headers=owner_headers,
    ).json()["id"]
    return owner_headers, owner_id, team_id, project_id


def test_task_api_create_list_detail_subtask_work_log_and_blocker_flow(client):
    owner_headers, owner_id, _team_id, project_id = create_api_project(client)
    task = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={
            "title": "API task",
            "owner_id": owner_id,
            "participant_ids": [],
            "task_type": "CODE",
            "priority": "HIGH",
            "labels": ["backend"],
        },
        headers=owner_headers,
    )
    task_id = task.json()["id"]
    listed = client.get(f"/api/v1/projects/{project_id}/tasks", headers=owner_headers)
    subtask = client.post(f"/api/v1/tasks/{task_id}/subtasks", json={"title": "Write tests"}, headers=owner_headers)
    completed = client.patch(
        f"/api/v1/tasks/{task_id}/subtasks/{subtask.json()['id']}",
        json={"is_completed": True},
        headers=owner_headers,
    )
    work_log = client.post(
        f"/api/v1/tasks/{task_id}/work-logs",
        json={
            "work_date": date.today().isoformat(),
            "hours": 1,
            "content": "Blocked while wiring API",
            "is_blocked": True,
            "blocked_reason": "Waiting for route decision",
            "commit_hash": "abc123",
        },
        headers=owner_headers,
    )
    blocked_board = client.get(f"/api/v1/projects/{project_id}/tasks", headers=owner_headers)
    detail = client.get(f"/api/v1/tasks/{task_id}", headers=owner_headers)
    resolved = client.post(
        f"/api/v1/tasks/{task_id}/work-logs/{work_log.json()['id']}/resolve-blocker",
        json={"resolution_note": "Route decision approved"},
        headers=owner_headers,
    )

    assert task.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == "API task"
    assert subtask.status_code == 201
    assert completed.status_code == 200
    assert completed.json()["is_completed"] is True
    assert work_log.status_code == 201
    assert blocked_board.json()[0]["blocker_summary"]["current_blocker_summary"] == "Waiting for route decision"
    assert detail.status_code == 200
    assert detail.json()["work_logs"][0]["commit_hash"] == "abc123"
    assert detail.json()["blocker_summary"]["is_blocked"] is True
    assert resolved.status_code == 200
    assert resolved.json()["resolved_by_id"] == owner_id


def test_task_api_permissions_status_codes_and_no_acceptance_routes(client):
    owner_headers, owner_id, team_id, project_id = create_api_project(client)
    member_headers = auth_headers(client, "api-member@example.com", "Member")
    outsider_headers = auth_headers(client, "api-outsider@example.com", "Outsider")
    invitation = client.post(
        f"/api/v1/teams/{team_id}/invitations",
        json={"email": "api-member@example.com", "role": TeamRole.TEAM_MEMBER.value},
        headers=owner_headers,
    )
    client.post(f"/api/v1/teams/invitations/{invitation.json()['id']}/accept", headers=member_headers)
    member_id = current_user_id(client, member_headers)
    add_project_member = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": member_id, "role": ProjectRole.PROJECT_MEMBER.value},
        headers=owner_headers,
    )
    first = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First API task", "owner_id": owner_id, "participant_ids": [member_id]},
        headers=owner_headers,
    )
    second = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Second API task", "owner_id": owner_id, "participant_ids": []},
        headers=owner_headers,
    )
    task_id = first.json()["id"]
    updated = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated API task", "priority": "URGENT"},
        headers=owner_headers,
    )
    removed_participant = client.delete(f"/api/v1/tasks/{task_id}/participants/{member_id}", headers=owner_headers)
    readded_participant = client.post(
        f"/api/v1/tasks/{task_id}/participants",
        json={"user_id": member_id},
        headers=owner_headers,
    )
    dep = client.post(
        f"/api/v1/tasks/{task_id}/dependencies",
        json={"depends_on_task_id": second.json()["id"]},
        headers=owner_headers,
    )
    cycle = client.post(
        f"/api/v1/tasks/{second.json()['id']}/dependencies",
        json={"depends_on_task_id": task_id},
        headers=owner_headers,
    )
    future_log = client.post(
        f"/api/v1/tasks/{task_id}/work-logs",
        json={"work_date": "2999-01-01", "hours": 1, "content": "future"},
        headers=member_headers,
    )
    unauthenticated = client.post(
        f"/api/v1/tasks/{task_id}/work-logs",
        json={"work_date": date.today().isoformat(), "hours": 1, "content": "no auth"},
    )
    outsider_detail = client.get(f"/api/v1/tasks/{task_id}", headers=outsider_headers)
    missing = client.get("/api/v1/tasks/999999", headers=owner_headers)
    forbidden_delete = client.delete(f"/api/v1/tasks/{task_id}", headers=member_headers)
    done = client.patch(f"/api/v1/tasks/{task_id}/status", json={"status": "DONE"}, headers=member_headers)
    deleted = client.delete(f"/api/v1/tasks/{task_id}", headers=owner_headers)
    acceptance_submission = client.post(f"/api/v1/tasks/{task_id}/acceptance-submissions", headers=owner_headers)
    acceptance_review = client.post(f"/api/v1/tasks/{task_id}/acceptance-reviews", headers=owner_headers)

    assert add_project_member.status_code == 201
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated API task"
    assert updated.json()["priority"] == "URGENT"
    assert removed_participant.status_code == 200
    assert removed_participant.json()["removed_at"] is not None
    assert readded_participant.status_code == 201
    assert readded_participant.json()["removed_at"] is None
    assert dep.status_code == 201
    assert cycle.status_code == 409
    assert future_log.status_code in {400, 422}
    assert unauthenticated.status_code == 401
    assert outsider_detail.status_code == 403
    assert missing.status_code == 404
    assert forbidden_delete.status_code == 403
    assert done.status_code == 400
    assert deleted.status_code == 200
    assert acceptance_submission.status_code == 404
    assert acceptance_review.status_code == 404
