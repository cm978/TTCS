from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.auth import UserPublic
from app.schemas.project import BoardColumnPublic

TaskStatusValue = Literal["TODO", "IN_PROGRESS", "IN_REVIEW", "REJECTED", "DONE", "CLOSED", "DELETED"]
TaskTypeValue = Literal["GENERAL", "DOCUMENT", "CODE"]
TaskPriorityValue = Literal["URGENT", "HIGH", "MEDIUM", "LOW"]
TaskParticipantRoleValue = Literal["PARTICIPANT"]


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    task_type: TaskTypeValue = "GENERAL"
    priority: TaskPriorityValue = "MEDIUM"
    due_date: date | None = None
    owner_id: int
    participant_ids: list[int] = Field(default_factory=list, max_length=5)
    column_id: int | None = None
    status: TaskStatusValue = "TODO"
    labels: list[str] = Field(default_factory=list, max_length=12)

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, labels: list[str]) -> list[str]:
        cleaned = [label.strip() for label in labels if label.strip()]
        if any(len(label) > 24 for label in cleaned):
            raise ValueError("Task labels must be 24 characters or fewer")
        return cleaned

    @model_validator(mode="after")
    def validate_participant_count(self) -> "TaskCreateRequest":
        unique_participants = set(self.participant_ids)
        unique_participants.add(self.owner_id)
        if len(unique_participants) > 5:
            raise ValueError("Task participants cannot exceed 5 including Owner")
        self.participant_ids = list(dict.fromkeys(self.participant_ids))
        return self


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    task_type: TaskTypeValue | None = None
    priority: TaskPriorityValue | None = None
    due_date: date | None = None
    owner_id: int | None = None
    column_id: int | None = None
    labels: list[str] | None = Field(default=None, max_length=12)

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, labels: list[str] | None) -> list[str] | None:
        if labels is None:
            return labels
        cleaned = [label.strip() for label in labels if label.strip()]
        if any(len(label) > 24 for label in cleaned):
            raise ValueError("Task labels must be 24 characters or fewer")
        return cleaned


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatusValue
    column_id: int | None = None


class TaskParticipantAddRequest(BaseModel):
    user_id: int


class TaskParticipantPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user_id: int
    role: TaskParticipantRoleValue
    removed_at: datetime | None
    created_at: datetime
    user: UserPublic | None = None


class SubtaskCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    position: int | None = Field(default=None, ge=1)


class SubtaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    is_completed: bool | None = None
    position: int | None = Field(default=None, ge=1)


class SubtaskPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    title: str
    is_completed: bool
    completed_by_id: int | None
    completed_at: datetime | None
    position: int
    created_at: datetime
    updated_at: datetime


class TaskDependencyCreateRequest(BaseModel):
    depends_on_task_id: int


class TaskDependencyPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    depends_on_task_id: int
    created_at: datetime


class WorkLogCreateRequest(BaseModel):
    work_date: date
    hours: float = Field(ge=0.5, le=24)
    content: str = Field(min_length=2, max_length=2000)
    work_type: str = Field(default="GENERAL", min_length=2, max_length=50)
    is_blocked: bool = False
    blocked_reason: str | None = Field(default=None, max_length=500)
    commit_hash: str | None = Field(default=None, max_length=120)
    branch_name: str | None = Field(default=None, max_length=255)
    repository_url: str | None = Field(default=None, max_length=500)

    @field_validator("hours")
    @classmethod
    def validate_half_hour_increment(cls, hours: float) -> float:
        if (hours * 2) % 1 != 0:
            raise ValueError("Work-log hours must use 0.5 hour increments")
        return hours

    @model_validator(mode="after")
    def validate_blocked_reason(self) -> "WorkLogCreateRequest":
        if self.work_date > date.today():
            raise ValueError("Work-log date cannot be in the future")
        if self.is_blocked and len((self.blocked_reason or "").strip()) < 10:
            raise ValueError("Blocked reason must be at least 10 characters")
        return self


class WorkLogUpdateRequest(BaseModel):
    work_date: date | None = None
    hours: float | None = Field(default=None, ge=0.5, le=24)
    content: str | None = Field(default=None, min_length=2, max_length=2000)
    work_type: str | None = Field(default=None, min_length=2, max_length=50)
    is_blocked: bool | None = None
    blocked_reason: str | None = Field(default=None, max_length=500)
    commit_hash: str | None = Field(default=None, max_length=120)
    branch_name: str | None = Field(default=None, max_length=255)
    repository_url: str | None = Field(default=None, max_length=500)

    @field_validator("hours")
    @classmethod
    def validate_half_hour_increment(cls, hours: float | None) -> float | None:
        if hours is not None and (hours * 2) % 1 != 0:
            raise ValueError("Work-log hours must use 0.5 hour increments")
        return hours

    @model_validator(mode="after")
    def validate_update(self) -> "WorkLogUpdateRequest":
        if self.work_date and self.work_date > date.today():
            raise ValueError("Work-log date cannot be in the future")
        if self.is_blocked is True and len((self.blocked_reason or "").strip()) < 10:
            raise ValueError("Blocked reason must be at least 10 characters")
        return self


class BlockerResolveRequest(BaseModel):
    resolution_note: str = Field(min_length=10, max_length=500)


class WorkLogPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user_id: int
    work_date: date
    hours: float
    content: str
    work_type: str
    is_blocked: bool
    blocked_reason: str | None
    resolved_at: datetime | None
    resolved_by_id: int | None
    resolution_note: str | None
    commit_hash: str | None
    branch_name: str | None
    repository_url: str | None
    git_synced: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskBlockerSummary(BaseModel):
    is_blocked: bool
    current_blocker_summary: str | None
    unresolved_count: int = 0


class TaskPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    column_id: int
    owner_id: int
    title: str
    description: str | None
    task_type: TaskTypeValue
    status: TaskStatusValue
    priority: TaskPriorityValue
    due_date: date | None
    labels: list[str]
    progress: int
    is_blocked: bool
    current_blocker_summary: str | None
    acceptance_summary: str | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskBoardCard(TaskPublic):
    owner: UserPublic | None = None
    participants: list[TaskParticipantPublic] = Field(default_factory=list)
    subtask_total: int = 0
    subtask_completed: int = 0
    latest_work_log_at: datetime | None = None
    blocker_summary: TaskBlockerSummary | None = None


class TaskDetailResponse(TaskPublic):
    owner: UserPublic | None = None
    column: BoardColumnPublic | None = None
    participants: list[TaskParticipantPublic] = Field(default_factory=list)
    subtasks: list[SubtaskPublic] = Field(default_factory=list)
    dependencies: list[TaskDependencyPublic] = Field(default_factory=list)
    work_logs: list[WorkLogPublic] = Field(default_factory=list)
    blocker_summary: TaskBlockerSummary | None = None
