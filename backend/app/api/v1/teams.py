from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.team import (
    ActionResponse,
    TeamCreateRequest,
    TeamInvitationCreateRequest,
    TeamInvitationPublic,
    TeamMemberPublic,
    TeamMemberRoleUpdateRequest,
    TeamPublic,
)
from app.services.permissions import DomainNotFoundError, PermissionDeniedError
from app.services.team_service import (
    DuplicateInvitationError,
    DuplicateTeamError,
    InvalidRoleError,
    InvitationUnavailableError,
    LastProjectManagerInTeamError,
    LastTeamAdminError,
    TeamLimitExceededError,
    TeamService,
)

router = APIRouter()


def _member_public(db: Session, member) -> TeamMemberPublic:
    user = db.get(User, member.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return TeamMemberPublic(
        id=member.id,
        team_id=member.team_id,
        user=UserPublic.model_validate(user),
        role=member.role,
        created_at=member.created_at,
    )


def _team_error(exc: ValueError) -> HTTPException:
    if isinstance(exc, PermissionDeniedError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, DomainNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, (DuplicateTeamError, DuplicateInvitationError)):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(
        exc,
        (InvalidRoleError, InvitationUnavailableError, LastProjectManagerInTeamError, LastTeamAdminError, TeamLimitExceededError),
    ):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team operation failed")


@router.post("", response_model=TeamPublic, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TeamService(db).create_team(current_user, payload)
    except ValueError as exc:
        raise _team_error(exc) from exc


@router.get("", response_model=list[TeamPublic])
def list_teams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TeamService(db).list_my_teams(current_user)


@router.get("/my-invitations", response_model=list[TeamInvitationPublic])
def list_my_invitations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TeamService(db).list_my_invitations(current_user)


@router.post("/invitations/{invitation_id}/accept", response_model=TeamInvitationPublic)
def accept_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TeamService(db).accept_invitation(current_user, invitation_id)
    except ValueError as exc:
        raise _team_error(exc) from exc


@router.post("/invitations/{invitation_id}/cancel", response_model=TeamInvitationPublic)
def cancel_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TeamService(db).cancel_invitation(current_user, invitation_id)
    except ValueError as exc:
        raise _team_error(exc) from exc


@router.get("/{team_id}", response_model=TeamPublic)
def get_team(team_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return TeamService(db).get_team_for_user(current_user, team_id)
    except ValueError as exc:
        raise _team_error(exc) from exc


@router.get("/{team_id}/members", response_model=list[TeamMemberPublic])
def list_team_members(team_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        members = TeamService(db).list_team_members(current_user, team_id)
    except ValueError as exc:
        raise _team_error(exc) from exc
    return [_member_public(db, member) for member in members]


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberPublic)
def update_team_member_role(
    team_id: int,
    user_id: int,
    payload: TeamMemberRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        member = TeamService(db).update_member_role(current_user, team_id, user_id, payload.role)
    except ValueError as exc:
        raise _team_error(exc) from exc
    return _member_public(db, member)


@router.delete("/{team_id}/members/{user_id}", response_model=ActionResponse)
def remove_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        TeamService(db).remove_member(current_user, team_id, user_id)
    except ValueError as exc:
        raise _team_error(exc) from exc
    return ActionResponse(status="ok")


@router.post("/{team_id}/invitations", response_model=TeamInvitationPublic, status_code=status.HTTP_201_CREATED)
def invite_team_member(
    team_id: int,
    payload: TeamInvitationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TeamService(db).invite_member(current_user, team_id, payload)
    except ValueError as exc:
        raise _team_error(exc) from exc


@router.get("/{team_id}/invitations", response_model=list[TeamInvitationPublic])
def list_team_invitations(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TeamService(db).list_team_invitations(current_user, team_id)
    except ValueError as exc:
        raise _team_error(exc) from exc
