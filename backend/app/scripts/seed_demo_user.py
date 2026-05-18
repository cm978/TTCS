import os
from datetime import date
from types import SimpleNamespace

from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.project import Project
from app.models.task import Task
from app.models.team import Team
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService, DuplicateEmailError
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.team_service import DuplicateTeamError, TeamService
from app.services.work_log_service import WorkLogService


def payload(**kwargs):
    return SimpleNamespace(**kwargs)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    email = os.getenv("DEMO_USER_EMAIL", "demo@example.com")
    password = os.getenv("DEMO_USER_PASSWORD", "DemoPass123!")
    display_name = os.getenv("DEMO_USER_DISPLAY_NAME", "TTCS Demo User")

    with SessionLocal() as db:
        service = AuthService(db)
        try:
            user = service.register(RegisterRequest(email=email, password=password, display_name=display_name))
            print(f"Created local demo user: {email}")
        except DuplicateEmailError:
            user = service.get_by_email(email)
            print(f"Local demo user already exists: {email}")
        if user is None:
            raise RuntimeError("Demo user could not be loaded")

        team = db.scalar(select(Team).where(Team.name == "TTCS Demo Team"))
        if team is None:
            try:
                team = TeamService(db).create_team(user, payload(name="TTCS Demo Team", description="Local Phase 3 demo data"))
                print("Created local demo team: TTCS Demo Team")
            except DuplicateTeamError:
                team = db.scalar(select(Team).where(Team.name == "TTCS Demo Team"))

        if team is None:
            raise RuntimeError("Demo team could not be loaded")

        project = db.scalar(select(Project).where(Project.team_id == team.id, Project.name == "Phase 3 Demo Project"))
        if project is None:
            project = ProjectService(db).create_project(
                user,
                team.id,
                payload(name="Phase 3 Demo Project", description="Task execution, work-log, and blocker smoke project"),
            )
            print("Created local demo project: Phase 3 Demo Project")

        task_service = TaskService(db)
        work_log_service = WorkLogService(db)
        existing_tasks = task_service.db.scalar(select(Project).where(Project.id == project.id))
        if existing_tasks is None:
            raise RuntimeError("Demo project could not be reloaded")

        if not project.columns:
            db.refresh(project)

        existing_task = db.scalar(select(Task).where(Task.project_id == project.id, Task.title == "Phase 3 smoke task"))
        if existing_task is None:
            task = task_service.create_task(
                user,
                project.id,
                payload(
                    title="Phase 3 smoke task",
                    description="Create a real work log, blocker, and task detail trail for local review.",
                    owner_id=user.id,
                    participant_ids=[],
                    task_type="CODE",
                    priority="HIGH",
                    labels=["demo", "phase-3"],
                ),
            )
            task_service.create_subtask(user, task.id, payload(title="Open the task drawer"))
            task_service.create_subtask(user, task.id, payload(title="Record a blocker work log"))
            work_log_service.create_work_log(
                user,
                task.id,
                payload(
                    work_date=date.today(),
                    hours=1,
                    content="Created local Phase 3 demo task execution trail.",
                    work_type="DEMO",
                    is_blocked=True,
                    blocked_reason="Waiting for smoke reviewer confirmation",
                    commit_hash="demo-local",
                    branch_name="local-demo",
                    repository_url="",
                ),
            )
            print("Created local Phase 3 task/work-log/blocker demo data")


if __name__ == "__main__":
    main()
