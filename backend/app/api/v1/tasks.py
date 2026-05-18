from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.project import BoardColumn
from app.models.task import Subtask, Task, TaskDependency, TaskParticipant, WorkLog
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.project import BoardColumnPublic
from app.schemas.task import (
    BlockerResolveRequest,
    SubtaskCreateRequest,
    SubtaskPublic,
    SubtaskUpdateRequest,
    TaskBlockerSummary,
    TaskBoardCard,
    TaskCreateRequest,
    TaskDependencyCreateRequest,
    TaskDependencyPublic,
    TaskDetailResponse,
    TaskParticipantAddRequest,
    TaskParticipantPublic,
    TaskPublic,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
    WorkLogCreateRequest,
    WorkLogPublic,
    WorkLogUpdateRequest,
)
from app.schemas.team import ActionResponse
from app.services.permissions import DomainNotFoundError, PermissionDeniedError, can_view_team_project, ensure_task_visible
from app.services.task_service import (
    InvalidTaskPriorityError,
    InvalidTaskTypeError,
    TaskDependencyCycleError,
    TaskParticipantLimitError,
    TaskService,
)
from app.services.task_state import InvalidTaskStatusTransitionError
from app.services.work_log_service import WorkLogPermissionError, WorkLogService, WorkLogValidationError

router = APIRouter()


def _task_error(exc: ValueError) -> HTTPException:
    if isinstance(exc, PermissionDeniedError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, DomainNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, TaskDependencyCycleError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(
        exc,
        (
            InvalidTaskPriorityError,
            InvalidTaskStatusTransitionError,
            InvalidTaskTypeError,
            TaskParticipantLimitError,
            WorkLogPermissionError,
            WorkLogValidationError,
        ),
    ):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task operation failed")


def _user_public(db: Session, user_id: int) -> UserPublic | None:
    user = db.get(User, user_id)
    return UserPublic.model_validate(user) if user is not None else None


def _participant_public(db: Session, participant: TaskParticipant) -> TaskParticipantPublic:
    return TaskParticipantPublic(
        id=participant.id,
        task_id=participant.task_id,
        user_id=participant.user_id,
        role=participant.role,
        removed_at=participant.removed_at,
        created_at=participant.created_at,
        user=_user_public(db, participant.user_id),
    )


def _blocker_summary(db: Session, task: Task) -> TaskBlockerSummary:
    unresolved_count = WorkLogService(db).unresolved_blocker_count(task.id)
    return TaskBlockerSummary(
        is_blocked=task.is_blocked,
        current_blocker_summary=task.current_blocker_summary,
        unresolved_count=unresolved_count,
    )


def _task_board_card(db: Session, task: Task) -> TaskBoardCard:
    subtask_total = db.scalar(select(func.count()).select_from(Subtask).where(Subtask.task_id == task.id)) or 0
    subtask_completed = (
        db.scalar(
            select(func.count()).select_from(Subtask).where(Subtask.task_id == task.id, Subtask.is_completed.is_(True))
        )
        or 0
    )
    latest_work_log_at = db.scalar(
        select(WorkLog.created_at)
        .where(WorkLog.task_id == task.id, WorkLog.deleted_at.is_(None))
        .order_by(WorkLog.created_at.desc(), WorkLog.id.desc())
    )
    participants = list(
        db.scalars(
            select(TaskParticipant)
            .where(TaskParticipant.task_id == task.id, TaskParticipant.removed_at.is_(None))
            .order_by(TaskParticipant.created_at, TaskParticipant.id)
        )
    )
    return TaskBoardCard(
        **TaskPublic.model_validate(task).model_dump(),
        owner=_user_public(db, task.owner_id),
        participants=[_participant_public(db, participant) for participant in participants],
        subtask_total=subtask_total,
        subtask_completed=subtask_completed,
        latest_work_log_at=latest_work_log_at,
        blocker_summary=_blocker_summary(db, task),
    )


def _task_detail(db: Session, task: Task, actor: User) -> TaskDetailResponse:
    participants = list(
        db.scalars(
            select(TaskParticipant)
            .where(TaskParticipant.task_id == task.id)
            .order_by(TaskParticipant.removed_at.is_(None).desc(), TaskParticipant.created_at, TaskParticipant.id)
        )
    )
    subtasks = list(db.scalars(select(Subtask).where(Subtask.task_id == task.id).order_by(Subtask.position, Subtask.id)))
    dependencies = list(db.scalars(select(TaskDependency).where(TaskDependency.task_id == task.id).order_by(TaskDependency.id)))
    logs = WorkLogService(db).list_task_logs(actor, task.id, include_deleted=True)
    column = db.get(BoardColumn, task.column_id)
    return TaskDetailResponse(
        **TaskPublic.model_validate(task).model_dump(),
        owner=_user_public(db, task.owner_id),
        column=BoardColumnPublic.model_validate(column) if column is not None else None,
        participants=[_participant_public(db, participant) for participant in participants],
        subtasks=[SubtaskPublic.model_validate(subtask) for subtask in subtasks],
        dependencies=[TaskDependencyPublic.model_validate(dependency) for dependency in dependencies],
        work_logs=[WorkLogPublic.model_validate(log) for log in logs],
        blocker_summary=_blocker_summary(db, task),
    )


@router.post("/projects/{project_id}/tasks", response_model=TaskDetailResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    payload: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        task = TaskService(db).create_task(current_user, project_id, payload)
        return _task_detail(db, task, current_user)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.get("/projects/{project_id}/tasks", response_model=list[TaskBoardCard])
def list_project_tasks(
    project_id: int,
    status_filter: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if not can_view_team_project(db, current_user, project_id):
            raise PermissionDeniedError("Project access required")
    except ValueError as exc:
        raise _task_error(exc) from exc
    filters = [Task.project_id == project_id, Task.deleted_at.is_(None)]
    if status_filter:
        filters.append(Task.status == status_filter)
    tasks = list(db.scalars(select(Task).where(*filters).order_by(Task.created_at.desc(), Task.id.desc())))
    return [_task_board_card(db, task) for task in tasks]


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task_detail(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        task = ensure_task_visible(db, current_user, task_id)
        return _task_detail(db, task, current_user)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.patch("/tasks/{task_id}", response_model=TaskDetailResponse)
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        task = TaskService(db).update_task(current_user, task_id, payload)
        return _task_detail(db, task, current_user)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.patch("/tasks/{task_id}/status", response_model=TaskDetailResponse)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        task = TaskService(db).change_status(current_user, task_id, payload.status, payload.column_id)
        return _task_detail(db, task, current_user)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.delete("/tasks/{task_id}", response_model=ActionResponse)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        TaskService(db).soft_delete_task(current_user, task_id)
        return ActionResponse(status="ok")
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.post("/tasks/{task_id}/participants", response_model=TaskParticipantPublic, status_code=status.HTTP_201_CREATED)
def add_task_participant(
    task_id: int,
    payload: TaskParticipantAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        participant = TaskService(db).add_participant(current_user, task_id, payload.user_id)
        return _participant_public(db, participant)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.delete("/tasks/{task_id}/participants/{user_id}", response_model=TaskParticipantPublic)
def remove_task_participant(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        participant = TaskService(db).remove_participant(current_user, task_id, user_id)
        return _participant_public(db, participant)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.post("/tasks/{task_id}/subtasks", response_model=SubtaskPublic, status_code=status.HTTP_201_CREATED)
def create_subtask(
    task_id: int,
    payload: SubtaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).create_subtask(current_user, task_id, payload)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.patch("/tasks/{task_id}/subtasks/{subtask_id}", response_model=SubtaskPublic)
def update_subtask(
    task_id: int,
    subtask_id: int,
    payload: SubtaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        subtask = TaskService(db).update_subtask(current_user, subtask_id, payload)
        if subtask.task_id != task_id:
            raise DomainNotFoundError("Subtask not found")
        return subtask
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.delete("/tasks/{task_id}/subtasks/{subtask_id}", response_model=ActionResponse)
def delete_subtask(
    task_id: int,
    subtask_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        subtask = db.get(Subtask, subtask_id)
        if subtask is None or subtask.task_id != task_id:
            raise DomainNotFoundError("Subtask not found")
        TaskService(db).delete_subtask(current_user, subtask_id)
        return ActionResponse(status="ok")
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.post("/tasks/{task_id}/dependencies", response_model=TaskDependencyPublic, status_code=status.HTTP_201_CREATED)
def add_dependency(
    task_id: int,
    payload: TaskDependencyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).add_dependency(current_user, task_id, payload.depends_on_task_id)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.delete("/tasks/{task_id}/dependencies/{depends_on_task_id}", response_model=ActionResponse)
def remove_dependency(
    task_id: int,
    depends_on_task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        TaskService(db).remove_dependency(current_user, task_id, depends_on_task_id)
        return ActionResponse(status="ok")
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.get("/tasks/{task_id}/work-logs", response_model=list[WorkLogPublic])
def list_work_logs(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return WorkLogService(db).list_task_logs(current_user, task_id)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.post("/tasks/{task_id}/work-logs", response_model=WorkLogPublic, status_code=status.HTTP_201_CREATED)
def create_work_log(
    task_id: int,
    payload: WorkLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return WorkLogService(db).create_work_log(current_user, task_id, payload)
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.patch("/tasks/{task_id}/work-logs/{log_id}", response_model=WorkLogPublic)
def update_work_log(
    task_id: int,
    log_id: int,
    payload: WorkLogUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        log = WorkLogService(db).update_work_log(current_user, log_id, payload)
        if log.task_id != task_id:
            raise DomainNotFoundError("Work log not found")
        return log
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.delete("/tasks/{task_id}/work-logs/{log_id}", response_model=WorkLogPublic)
def delete_work_log(
    task_id: int,
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        log = WorkLogService(db).soft_delete_work_log(current_user, log_id)
        if log.task_id != task_id:
            raise DomainNotFoundError("Work log not found")
        return log
    except ValueError as exc:
        raise _task_error(exc) from exc


@router.post("/tasks/{task_id}/work-logs/{log_id}/resolve-blocker", response_model=WorkLogPublic)
def resolve_blocker(
    task_id: int,
    log_id: int,
    payload: BlockerResolveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        log = WorkLogService(db).resolve_blocker(current_user, log_id, payload)
        if log.task_id != task_id:
            raise DomainNotFoundError("Work log not found")
        return log
    except ValueError as exc:
        raise _task_error(exc) from exc
