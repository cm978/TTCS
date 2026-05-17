from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.project import (
    ProjectBoardResponse,
    ProjectCreateRequest,
    ProjectMemberAddRequest,
    ProjectMemberPublic,
    ProjectMemberRoleUpdateRequest,
    ProjectPublic,
)
from app.schemas.team import ActionResponse
from app.services.permissions import DomainNotFoundError, PermissionDeniedError
from app.services.project_service import (
    DuplicateProjectMemberError,
    InvalidProjectRoleError,
    LastProjectManagerError,
    ProjectDateError,
    ProjectService,
)

router = APIRouter()


def _project_error(exc: ValueError) -> HTTPException:
    if isinstance(exc, PermissionDeniedError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, DomainNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, DuplicateProjectMemberError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, (InvalidProjectRoleError, LastProjectManagerError, ProjectDateError)):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project operation failed")


def _member_public(db: Session, member) -> ProjectMemberPublic:
    user = db.get(User, member.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ProjectMemberPublic(
        id=member.id,
        project_id=member.project_id,
        user=UserPublic.model_validate(user),
        role=member.role,
        created_at=member.created_at,
    )


@router.post("/teams/{team_id}/projects", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
def create_project(
    team_id: int,
    payload: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return ProjectService(db).create_project(current_user, team_id, payload)
    except ValueError as exc:
        raise _project_error(exc) from exc


@router.get("/projects", response_model=list[ProjectPublic])
def list_projects(
    team_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService(db).list_accessible_projects(current_user, team_id)


@router.get("/projects/{project_id}/board", response_model=ProjectBoardResponse)
def get_project_board(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        project = ProjectService(db).get_project_board(current_user, project_id)
        members = ProjectService(db).list_project_members(current_user, project_id)
    except ValueError as exc:
        raise _project_error(exc) from exc
    return ProjectBoardResponse(
        project=ProjectPublic.model_validate(project),
        members=[_member_public(db, member) for member in members],
        columns=list(project.columns),
    )


@router.get("/projects/{project_id}/members", response_model=list[ProjectMemberPublic])
def list_project_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        members = ProjectService(db).list_project_members(current_user, project_id)
    except ValueError as exc:
        raise _project_error(exc) from exc
    return [_member_public(db, member) for member in members]


@router.post("/projects/{project_id}/members", response_model=ProjectMemberPublic, status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: int,
    payload: ProjectMemberAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        member = ProjectService(db).add_project_member(current_user, project_id, payload.user_id, payload.role)
    except ValueError as exc:
        raise _project_error(exc) from exc
    return _member_public(db, member)


@router.patch("/projects/{project_id}/members/{user_id}", response_model=ProjectMemberPublic)
def update_project_member_role(
    project_id: int,
    user_id: int,
    payload: ProjectMemberRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        member = ProjectService(db).update_project_member_role(current_user, project_id, user_id, payload.role)
    except ValueError as exc:
        raise _project_error(exc) from exc
    return _member_public(db, member)


@router.delete("/projects/{project_id}/members/{user_id}", response_model=ActionResponse)
def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ProjectService(db).remove_project_member(current_user, project_id, user_id)
    except ValueError as exc:
        raise _project_error(exc) from exc
    return ActionResponse(status="ok")
