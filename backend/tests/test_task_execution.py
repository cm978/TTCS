from app.models.task import TaskPriority, TaskStatus, TaskType


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
