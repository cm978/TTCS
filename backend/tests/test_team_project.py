from types import SimpleNamespace

import pytest

from app.core.security import hash_password
from app.models.project import BoardColumnStatus, ProjectMember, ProjectRole
from app.models.team import TeamInvitationStatus, TeamMember, TeamRole
from app.models.user import User
from app.services.permissions import PermissionDeniedError
from app.services.project_service import LastProjectManagerError, ProjectService
from app.services.team_service import DuplicateInvitationError, LastTeamAdminError, TeamService


def make_user(db_session, email: str, display_name: str = "User") -> User:
    user = User(email=email, display_name=display_name, hashed_password=hash_password("SecurePass123!"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def payload(**kwargs):
    return SimpleNamespace(**kwargs)


def test_create_team_adds_creator_as_admin(db_session):
    user = make_user(db_session, "owner@example.com")

    team = TeamService(db_session).create_team(user, payload(name="Demo Team", description="Phase 2"))

    membership = db_session.query(TeamMember).filter_by(team_id=team.id, user_id=user.id).one()
    assert team.name == "Demo Team"
    assert membership.role == TeamRole.TEAM_ADMIN.value


def test_invitation_acceptance_matches_normalized_email_and_role(db_session):
    owner = make_user(db_session, "owner@example.com")
    invited = make_user(db_session, "Member@Example.com")
    service = TeamService(db_session)
    team = service.create_team(owner, payload(name="Demo Team", description=None))

    invitation = service.invite_member(
        owner,
        team.id,
        payload(email=" member@example.com ", role=TeamRole.TEAM_MEMBER.value),
    )

    with pytest.raises(DuplicateInvitationError):
        service.invite_member(owner, team.id, payload(email="MEMBER@example.com", role=TeamRole.TEAM_MEMBER.value))

    accepted = service.accept_invitation(invited, invitation.id)

    membership = db_session.query(TeamMember).filter_by(team_id=team.id, user_id=invited.id).one()
    assert accepted.status == TeamInvitationStatus.ACCEPTED.value
    assert membership.role == TeamRole.TEAM_MEMBER.value


def test_accept_invitation_rejects_wrong_user_email(db_session):
    owner = make_user(db_session, "owner@example.com")
    wrong_user = make_user(db_session, "wrong@example.com")
    service = TeamService(db_session)
    team = service.create_team(owner, payload(name="Demo Team", description=None))
    invitation = service.invite_member(owner, team.id, payload(email="member@example.com", role=TeamRole.TEAM_MEMBER.value))

    with pytest.raises(PermissionDeniedError):
        service.accept_invitation(wrong_user, invitation.id)


def test_team_must_keep_one_admin(db_session):
    owner = make_user(db_session, "owner@example.com")
    service = TeamService(db_session)
    team = service.create_team(owner, payload(name="Demo Team", description=None))

    with pytest.raises(LastTeamAdminError):
        service.update_member_role(owner, team.id, owner.id, TeamRole.TEAM_MEMBER.value)

    with pytest.raises(LastTeamAdminError):
        service.remove_member(owner, team.id, owner.id)


def test_project_creation_adds_manager_and_default_columns(db_session):
    owner = make_user(db_session, "owner@example.com")
    team = TeamService(db_session).create_team(owner, payload(name="Demo Team", description=None))

    project = ProjectService(db_session).create_project(owner, team.id, payload(name="Launch", description=None))

    membership = db_session.query(ProjectMember).filter_by(project_id=project.id, user_id=owner.id).one()
    statuses = [column.status for column in project.columns]
    assert membership.role == ProjectRole.PROJECT_MANAGER.value
    assert statuses == [
        BoardColumnStatus.TODO.value,
        BoardColumnStatus.IN_PROGRESS.value,
        BoardColumnStatus.IN_REVIEW.value,
        BoardColumnStatus.REJECTED.value,
        BoardColumnStatus.DONE.value,
    ]


def test_project_member_must_belong_to_team(db_session):
    owner = make_user(db_session, "owner@example.com")
    outsider = make_user(db_session, "outsider@example.com")
    team = TeamService(db_session).create_team(owner, payload(name="Demo Team", description=None))
    project = ProjectService(db_session).create_project(owner, team.id, payload(name="Launch", description=None))

    with pytest.raises(PermissionDeniedError):
        ProjectService(db_session).add_project_member(owner, project.id, outsider.id, ProjectRole.PROJECT_MEMBER.value)


def test_team_admin_can_view_but_not_manage_project_without_project_role(db_session):
    owner = make_user(db_session, "owner@example.com")
    admin = make_user(db_session, "admin@example.com")
    team_service = TeamService(db_session)
    team = team_service.create_team(owner, payload(name="Demo Team", description=None))
    invitation = team_service.invite_member(owner, team.id, payload(email=admin.email, role=TeamRole.TEAM_ADMIN.value))
    team_service.accept_invitation(admin, invitation.id)
    project = ProjectService(db_session).create_project(owner, team.id, payload(name="Launch", description=None))

    visible = ProjectService(db_session).get_project_board(admin, project.id)
    assert visible.id == project.id

    with pytest.raises(PermissionDeniedError):
        ProjectService(db_session).add_project_member(admin, project.id, admin.id, ProjectRole.PROJECT_MEMBER.value)


def test_project_must_keep_one_manager(db_session):
    owner = make_user(db_session, "owner@example.com")
    team = TeamService(db_session).create_team(owner, payload(name="Demo Team", description=None))
    project = ProjectService(db_session).create_project(owner, team.id, payload(name="Launch", description=None))

    with pytest.raises(LastProjectManagerError):
        ProjectService(db_session).update_project_member_role(owner, project.id, owner.id, ProjectRole.PROJECT_MEMBER.value)

    with pytest.raises(LastProjectManagerError):
        ProjectService(db_session).remove_project_member(owner, project.id, owner.id)
