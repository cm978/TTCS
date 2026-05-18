from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import BoardColumn, BoardColumnStatus, ProjectMember, ProjectRole
from app.models.task import (
    Subtask,
    Task,
    TaskDependency,
    TaskParticipant,
    TaskParticipantRole,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from app.models.user import User
from app.services.permissions import (
    DomainNotFoundError,
    PermissionDeniedError,
    can_manage_task_participants,
    ensure_project_manager,
    ensure_project_member,
    ensure_task_owner_or_project_manager,
    ensure_task_participant_or_owner,
)
from app.services.task_state import InvalidTaskStatusTransitionError, validate_phase3_transition

MAX_TASK_PARTICIPANTS = 5


class TaskNotFoundError(DomainNotFoundError):
    pass


class TaskPermissionError(PermissionDeniedError):
    pass


class TaskParticipantLimitError(ValueError):
    pass


class TaskDependencyCycleError(ValueError):
    pass


class InvalidTaskTypeError(ValueError):
    pass


class InvalidTaskPriorityError(ValueError):
    pass


def _value(payload: Any, name: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        return payload.get(name, default)
    return getattr(payload, name, default)


def _provided(payload: Any, name: str) -> bool:
    if isinstance(payload, dict):
        return name in payload
    return hasattr(payload, name)


def _validate_task_type(task_type: str) -> str:
    if task_type not in {item.value for item in TaskType}:
        raise InvalidTaskTypeError("Invalid task type")
    return task_type


def _validate_priority(priority: str) -> str:
    if priority not in {item.value for item in TaskPriority}:
        raise InvalidTaskPriorityError("Invalid task priority")
    return priority


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_task(self, actor: User, project_id: int, payload: Any) -> Task:
        ensure_project_member(self.db, actor, project_id)
        owner_id = int(_value(payload, "owner_id"))
        self._ensure_project_member_user(project_id, owner_id)
        participant_ids = self._normalized_participant_ids(owner_id, _value(payload, "participant_ids", []))
        self._ensure_participant_limit(participant_ids)
        for user_id in participant_ids:
            self._ensure_project_member_user(project_id, user_id)

        column = self._resolve_column(project_id, _value(payload, "column_id"), _value(payload, "status", TaskStatus.TODO.value))
        if column.status != TaskStatus.TODO.value:
            raise InvalidTaskStatusTransitionError("New Phase 3 tasks must start in TODO")
        task = Task(
            project_id=project_id,
            column_id=column.id,
            owner_id=owner_id,
            title=str(_value(payload, "title", "")).strip(),
            description=_value(payload, "description"),
            task_type=_validate_task_type(_value(payload, "task_type", TaskType.GENERAL.value)),
            status=column.status,
            priority=_validate_priority(_value(payload, "priority", TaskPriority.MEDIUM.value)),
            due_date=_value(payload, "due_date"),
            labels=list(_value(payload, "labels", []) or []),
            progress=0,
            is_blocked=False,
            acceptance_summary=_value(payload, "acceptance_summary"),
        )
        self.db.add(task)
        self.db.flush()
        for user_id in participant_ids:
            self.db.add(
                TaskParticipant(
                    task_id=task.id,
                    user_id=user_id,
                    role=TaskParticipantRole.PARTICIPANT.value,
                )
            )
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task(self, actor: User, task_id: int, payload: Any) -> Task:
        task = ensure_task_owner_or_project_manager(self.db, actor, task_id)
        if _provided(payload, "title") and _value(payload, "title") is not None:
            task.title = str(_value(payload, "title")).strip()
        if _provided(payload, "description"):
            task.description = _value(payload, "description")
        if _provided(payload, "task_type") and _value(payload, "task_type") is not None:
            task.task_type = _validate_task_type(_value(payload, "task_type"))
        if _provided(payload, "priority") and _value(payload, "priority") is not None:
            task.priority = _validate_priority(_value(payload, "priority"))
        if _provided(payload, "due_date"):
            task.due_date = _value(payload, "due_date")
        if _provided(payload, "labels") and _value(payload, "labels") is not None:
            task.labels = list(_value(payload, "labels") or [])
        if _provided(payload, "owner_id") and _value(payload, "owner_id") is not None:
            owner_id = int(_value(payload, "owner_id"))
            self._ensure_project_member_user(task.project_id, owner_id)
            task.owner_id = owner_id
            self._ensure_active_participant(task, owner_id)
        if _provided(payload, "column_id") and _value(payload, "column_id") is not None:
            column = self._get_project_column(task.project_id, int(_value(payload, "column_id")))
            validate_phase3_transition(task, column.status)
            task.column_id = column.id
            task.status = column.status
        self.db.commit()
        self.db.refresh(task)
        return task

    def soft_delete_task(self, actor: User, task_id: int) -> Task:
        task = self._get_task(task_id)
        ensure_project_manager(self.db, actor, task.project_id)
        task.deleted_at = _now()
        task.status = TaskStatus.DELETED.value
        self.db.commit()
        self.db.refresh(task)
        return task

    def change_status(self, actor: User, task_id: int, target_status: str, column_id: int | None = None) -> Task:
        task = ensure_task_participant_or_owner(self.db, actor, task_id)
        validate_phase3_transition(task, target_status)
        column = self._resolve_column(task.project_id, column_id, target_status)
        task.status = target_status
        task.column_id = column.id
        self.db.commit()
        self.db.refresh(task)
        return task

    def add_participant(self, actor: User, task_id: int, user_id: int) -> TaskParticipant:
        task = ensure_task_owner_or_project_manager(self.db, actor, task_id)
        if not can_manage_task_participants(self.db, actor, task):
            raise TaskPermissionError("Task participant management required")
        self._ensure_project_member_user(task.project_id, user_id)
        participant = self._find_participant(task_id, user_id)
        if participant is not None and participant.removed_at is None:
            return participant
        active_count = self._active_participant_count(task_id)
        if participant is None and active_count >= MAX_TASK_PARTICIPANTS:
            raise TaskParticipantLimitError("Task participants cannot exceed 5 including Owner")
        if participant is not None:
            if active_count >= MAX_TASK_PARTICIPANTS:
                raise TaskParticipantLimitError("Task participants cannot exceed 5 including Owner")
            participant.removed_at = None
        else:
            participant = TaskParticipant(task_id=task_id, user_id=user_id, role=TaskParticipantRole.PARTICIPANT.value)
            self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def remove_participant(self, actor: User, task_id: int, user_id: int) -> TaskParticipant:
        task = ensure_task_owner_or_project_manager(self.db, actor, task_id)
        if not can_manage_task_participants(self.db, actor, task):
            raise TaskPermissionError("Task participant management required")
        participant = self._find_participant(task_id, user_id)
        if participant is None or participant.removed_at is not None:
            raise DomainNotFoundError("Task participant not found")
        participant.removed_at = _now()
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def create_subtask(self, actor: User, task_id: int, payload: Any) -> Subtask:
        task = ensure_task_participant_or_owner(self.db, actor, task_id)
        position = _value(payload, "position")
        if position is None:
            position = (self.db.scalar(select(func.max(Subtask.position)).where(Subtask.task_id == task.id)) or 0) + 1
        subtask = Subtask(task_id=task.id, title=str(_value(payload, "title", "")).strip(), position=int(position))
        self.db.add(subtask)
        self.db.flush()
        self.recalculate_progress(task.id, commit=False)
        self.db.commit()
        self.db.refresh(subtask)
        return subtask

    def update_subtask(self, actor: User, subtask_id: int, payload: Any) -> Subtask:
        subtask = self._get_subtask(subtask_id)
        ensure_task_participant_or_owner(self.db, actor, subtask.task_id)
        if _provided(payload, "title") and _value(payload, "title") is not None:
            subtask.title = str(_value(payload, "title")).strip()
        if _provided(payload, "position") and _value(payload, "position") is not None:
            subtask.position = int(_value(payload, "position"))
        if _provided(payload, "is_completed") and _value(payload, "is_completed") is not None:
            is_completed = bool(_value(payload, "is_completed"))
            subtask.is_completed = is_completed
            subtask.completed_by_id = actor.id if is_completed else None
            subtask.completed_at = _now() if is_completed else None
        self.recalculate_progress(subtask.task_id, commit=False)
        self.db.commit()
        self.db.refresh(subtask)
        return subtask

    def delete_subtask(self, actor: User, subtask_id: int) -> None:
        subtask = self._get_subtask(subtask_id)
        task_id = subtask.task_id
        ensure_task_participant_or_owner(self.db, actor, task_id)
        self.db.delete(subtask)
        self.db.flush()
        self.recalculate_progress(task_id, commit=False)
        self.db.commit()

    def add_dependency(self, actor: User, task_id: int, depends_on_task_id: int) -> TaskDependency:
        task = ensure_task_owner_or_project_manager(self.db, actor, task_id)
        dependency_task = self._get_task(depends_on_task_id)
        if task.project_id != dependency_task.project_id:
            raise PermissionDeniedError("Task dependency must be in the same project")
        if task.id == dependency_task.id:
            raise TaskDependencyCycleError("Task cannot depend on itself")
        if self._would_create_cycle(task.id, dependency_task.id):
            raise TaskDependencyCycleError("Task dependency cycle detected")
        existing = self.db.scalar(
            select(TaskDependency).where(
                TaskDependency.task_id == task.id,
                TaskDependency.depends_on_task_id == dependency_task.id,
            )
        )
        if existing is not None:
            return existing
        dependency = TaskDependency(task_id=task.id, depends_on_task_id=dependency_task.id)
        self.db.add(dependency)
        self.db.commit()
        self.db.refresh(dependency)
        return dependency

    def remove_dependency(self, actor: User, task_id: int, depends_on_task_id: int) -> None:
        task = ensure_task_owner_or_project_manager(self.db, actor, task_id)
        dependency = self.db.scalar(
            select(TaskDependency).where(
                TaskDependency.task_id == task.id,
                TaskDependency.depends_on_task_id == depends_on_task_id,
            )
        )
        if dependency is None:
            raise DomainNotFoundError("Task dependency not found")
        self.db.delete(dependency)
        self.db.commit()

    def recalculate_progress(self, task_id: int, commit: bool = True) -> int:
        task = self._get_task(task_id)
        subtasks = list(self.db.scalars(select(Subtask).where(Subtask.task_id == task_id)))
        if not subtasks:
            task.progress = 0
        else:
            completed = sum(1 for subtask in subtasks if subtask.is_completed)
            task.progress = round(completed / len(subtasks) * 100)
        if commit:
            self.db.commit()
            self.db.refresh(task)
        return task.progress

    def _get_task(self, task_id: int) -> Task:
        task = self.db.get(Task, task_id)
        if task is None or task.deleted_at is not None:
            raise TaskNotFoundError("Task not found")
        return task

    def _get_subtask(self, subtask_id: int) -> Subtask:
        subtask = self.db.get(Subtask, subtask_id)
        if subtask is None:
            raise DomainNotFoundError("Subtask not found")
        return subtask

    def _get_project_column(self, project_id: int, column_id: int) -> BoardColumn:
        column = self.db.get(BoardColumn, column_id)
        if column is None or column.project_id != project_id:
            raise DomainNotFoundError("Board column not found")
        return column

    def _resolve_column(self, project_id: int, column_id: int | None, status: str) -> BoardColumn:
        if column_id is not None:
            return self._get_project_column(project_id, int(column_id))
        if status not in {column_status.value for column_status in BoardColumnStatus}:
            status = TaskStatus.TODO.value
        column = self.db.scalar(select(BoardColumn).where(BoardColumn.project_id == project_id, BoardColumn.status == status))
        if column is None:
            raise DomainNotFoundError("Board column not found")
        return column

    def _ensure_project_member_user(self, project_id: int, user_id: int) -> ProjectMember:
        membership = self.db.scalar(
            select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        )
        if membership is None:
            raise PermissionDeniedError("Task user must be a project member")
        return membership

    def _normalized_participant_ids(self, owner_id: int, participant_ids: list[int] | tuple[int, ...]) -> list[int]:
        normalized: list[int] = []
        for user_id in [owner_id, *(participant_ids or [])]:
            if user_id not in normalized:
                normalized.append(int(user_id))
        return normalized

    def _ensure_participant_limit(self, participant_ids: list[int]) -> None:
        if len(participant_ids) > MAX_TASK_PARTICIPANTS:
            raise TaskParticipantLimitError("Task participants cannot exceed 5 including Owner")

    def _find_participant(self, task_id: int, user_id: int) -> TaskParticipant | None:
        return self.db.scalar(select(TaskParticipant).where(TaskParticipant.task_id == task_id, TaskParticipant.user_id == user_id))

    def _ensure_active_participant(self, task: Task, user_id: int) -> TaskParticipant:
        participant = self._find_participant(task.id, user_id)
        if participant is not None:
            participant.removed_at = None
            return participant
        if self._active_participant_count(task.id) >= MAX_TASK_PARTICIPANTS:
            raise TaskParticipantLimitError("Task participants cannot exceed 5 including Owner")
        participant = TaskParticipant(task_id=task.id, user_id=user_id, role=TaskParticipantRole.PARTICIPANT.value)
        self.db.add(participant)
        return participant

    def _active_participant_count(self, task_id: int) -> int:
        return (
            self.db.scalar(
                select(func.count()).select_from(TaskParticipant).where(
                    TaskParticipant.task_id == task_id,
                    TaskParticipant.removed_at.is_(None),
                )
            )
            or 0
        )

    def _would_create_cycle(self, task_id: int, depends_on_task_id: int) -> bool:
        stack = [depends_on_task_id]
        seen: set[int] = set()
        while stack:
            current = stack.pop()
            if current == task_id:
                return True
            if current in seen:
                continue
            seen.add(current)
            next_ids = self.db.scalars(
                select(TaskDependency.depends_on_task_id).where(TaskDependency.task_id == current)
            )
            stack.extend(next_ids)
        return False
