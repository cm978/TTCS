from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task, WorkLog
from app.models.user import User
from app.services.permissions import (
    DomainNotFoundError,
    PermissionDeniedError,
    can_manage_task_participants,
    ensure_task_participant_or_owner,
    ensure_task_visible,
)


class WorkLogValidationError(ValueError):
    pass


class WorkLogPermissionError(PermissionDeniedError):
    pass


def _value(payload: Any, name: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        return payload.get(name, default)
    return getattr(payload, name, default)


def _provided(payload: Any, name: str) -> bool:
    if isinstance(payload, dict):
        return name in payload
    return hasattr(payload, name)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_work_date(work_date: date) -> date:
    if work_date > date.today():
        raise WorkLogValidationError("Work-log date cannot be in the future")
    return work_date


def _validate_hours(hours: float) -> float:
    if hours < 0.5 or hours > 24:
        raise WorkLogValidationError("Work-log hours must be between 0.5 and 24")
    if (hours * 2) % 1 != 0:
        raise WorkLogValidationError("Work-log hours must use 0.5 hour increments")
    return hours


def _validate_blocked_reason(is_blocked: bool, blocked_reason: str | None) -> str | None:
    if is_blocked and len((blocked_reason or "").strip()) < 10:
        raise WorkLogValidationError("Blocked reason must be at least 10 characters")
    return blocked_reason.strip() if blocked_reason else None


def _validate_resolution_note(note: str) -> str:
    if len(note.strip()) < 10:
        raise WorkLogValidationError("Resolution note must be at least 10 characters")
    return note.strip()


class WorkLogService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_work_log(self, actor: User, task_id: int, payload: Any) -> WorkLog:
        task = ensure_task_participant_or_owner(self.db, actor, task_id)
        is_blocked = bool(_value(payload, "is_blocked", False))
        work_log = WorkLog(
            task_id=task.id,
            user_id=actor.id,
            work_date=_validate_work_date(_value(payload, "work_date")),
            hours=_validate_hours(float(_value(payload, "hours"))),
            content=str(_value(payload, "content", "")).strip(),
            work_type=str(_value(payload, "work_type", "GENERAL")).strip() or "GENERAL",
            is_blocked=is_blocked,
            blocked_reason=_validate_blocked_reason(is_blocked, _value(payload, "blocked_reason")),
            commit_hash=_value(payload, "commit_hash"),
            branch_name=_value(payload, "branch_name"),
            repository_url=_value(payload, "repository_url"),
            git_synced=False,
        )
        if not work_log.content:
            raise WorkLogValidationError("Work-log content is required")
        self.db.add(work_log)
        self.db.flush()
        self.recompute_task_blocker_state(task.id, commit=False)
        self.db.commit()
        self.db.refresh(work_log)
        return work_log

    def update_work_log(self, actor: User, log_id: int, payload: Any) -> WorkLog:
        work_log = self._get_work_log(log_id)
        self._ensure_log_creator(actor, work_log)
        if _provided(payload, "work_date") and _value(payload, "work_date") is not None:
            work_log.work_date = _validate_work_date(_value(payload, "work_date"))
        if _provided(payload, "hours") and _value(payload, "hours") is not None:
            work_log.hours = _validate_hours(float(_value(payload, "hours")))
        if _provided(payload, "content") and _value(payload, "content") is not None:
            work_log.content = str(_value(payload, "content")).strip()
        if _provided(payload, "work_type") and _value(payload, "work_type") is not None:
            work_log.work_type = str(_value(payload, "work_type")).strip() or "GENERAL"
        if _provided(payload, "is_blocked") and _value(payload, "is_blocked") is not None:
            work_log.is_blocked = bool(_value(payload, "is_blocked"))
            if not work_log.is_blocked:
                work_log.resolved_at = None
                work_log.resolved_by_id = None
                work_log.resolution_note = None
        if _provided(payload, "blocked_reason"):
            work_log.blocked_reason = _validate_blocked_reason(work_log.is_blocked, _value(payload, "blocked_reason"))
        if _provided(payload, "commit_hash"):
            work_log.commit_hash = _value(payload, "commit_hash")
        if _provided(payload, "branch_name"):
            work_log.branch_name = _value(payload, "branch_name")
        if _provided(payload, "repository_url"):
            work_log.repository_url = _value(payload, "repository_url")
        self.recompute_task_blocker_state(work_log.task_id, commit=False)
        self.db.commit()
        self.db.refresh(work_log)
        return work_log

    def soft_delete_work_log(self, actor: User, log_id: int) -> WorkLog:
        work_log = self._get_work_log(log_id)
        self._ensure_log_creator(actor, work_log)
        work_log.deleted_at = _now()
        self.recompute_task_blocker_state(work_log.task_id, commit=False)
        self.db.commit()
        self.db.refresh(work_log)
        return work_log

    def list_task_logs(self, actor: User, task_id: int, include_deleted: bool = False) -> list[WorkLog]:
        task = ensure_task_visible(self.db, actor, task_id)
        filters = [WorkLog.task_id == task.id]
        if not include_deleted:
            filters.append(WorkLog.deleted_at.is_(None))
        return list(
            self.db.scalars(
                select(WorkLog)
                .where(*filters)
                .order_by(WorkLog.work_date.desc(), WorkLog.created_at.desc(), WorkLog.id.desc())
            )
        )

    def resolve_blocker(self, actor: User, log_id: int, payload: Any) -> WorkLog:
        work_log = self._get_work_log(log_id)
        task = ensure_task_visible(self.db, actor, work_log.task_id)
        if not work_log.is_blocked:
            raise WorkLogValidationError("Work log is not a blocker")
        if work_log.deleted_at is not None:
            raise WorkLogValidationError("Deleted work log cannot be resolved")
        if work_log.user_id != actor.id and not can_manage_task_participants(self.db, actor, task):
            raise WorkLogPermissionError("Blocker creator, task Owner, or project manager required")
        work_log.resolved_at = _now()
        work_log.resolved_by_id = actor.id
        work_log.resolution_note = _validate_resolution_note(_value(payload, "resolution_note", ""))
        self.recompute_task_blocker_state(work_log.task_id, commit=False)
        self.db.commit()
        self.db.refresh(work_log)
        return work_log

    def recompute_task_blocker_state(self, task_id: int, commit: bool = True) -> Task:
        task = self.db.get(Task, task_id)
        if task is None:
            raise DomainNotFoundError("Task not found")
        self.db.flush()
        latest_unresolved = self.db.scalar(
            select(WorkLog)
            .where(
                WorkLog.task_id == task_id,
                WorkLog.is_blocked.is_(True),
                WorkLog.resolved_at.is_(None),
                WorkLog.deleted_at.is_(None),
            )
            .order_by(WorkLog.created_at.desc(), WorkLog.id.desc())
        )
        task.is_blocked = latest_unresolved is not None
        task.current_blocker_summary = latest_unresolved.blocked_reason if latest_unresolved is not None else None
        if commit:
            self.db.commit()
            self.db.refresh(task)
        return task

    def can_submit_acceptance_preview(self, task_id: int) -> bool:
        task = self.db.get(Task, task_id)
        if task is None:
            raise DomainNotFoundError("Task not found")
        self.recompute_task_blocker_state(task_id)
        return not task.is_blocked

    def unresolved_blocker_count(self, task_id: int) -> int:
        return len(
            list(
                self.db.scalars(
                    select(WorkLog.id).where(
                        WorkLog.task_id == task_id,
                        WorkLog.is_blocked.is_(True),
                        WorkLog.resolved_at.is_(None),
                        WorkLog.deleted_at.is_(None),
                    )
                )
            )
        )

    def _get_work_log(self, log_id: int) -> WorkLog:
        work_log = self.db.get(WorkLog, log_id)
        if work_log is None:
            raise DomainNotFoundError("Work log not found")
        return work_log

    def _ensure_log_creator(self, actor: User, work_log: WorkLog) -> None:
        if work_log.user_id != actor.id:
            raise WorkLogPermissionError("Only the work-log creator can edit this log")
