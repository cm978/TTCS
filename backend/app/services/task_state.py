from app.models.task import Task, TaskStatus


ALLOWED_PHASE3_TRANSITIONS: dict[str, set[str]] = {
    TaskStatus.TODO.value: {TaskStatus.IN_PROGRESS.value},
    TaskStatus.REJECTED.value: {TaskStatus.IN_PROGRESS.value},
}

PHASE3_RESERVED_TARGETS = {
    TaskStatus.IN_REVIEW.value,
    TaskStatus.REJECTED.value,
    TaskStatus.DONE.value,
    TaskStatus.CLOSED.value,
    TaskStatus.DELETED.value,
}


class InvalidTaskStatusTransitionError(ValueError):
    pass


def validate_phase3_transition(task: Task, target_status: str) -> None:
    if task.status == target_status:
        return
    if target_status in PHASE3_RESERVED_TARGETS:
        raise InvalidTaskStatusTransitionError("Phase 3 task actions cannot move tasks into review, done, or closed states")
    allowed = ALLOWED_PHASE3_TRANSITIONS.get(task.status, set())
    if target_status not in allowed:
        raise InvalidTaskStatusTransitionError("Invalid Phase 3 task status transition")
