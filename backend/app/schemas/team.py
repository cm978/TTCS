from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.auth import UserPublic

TeamRoleValue = Literal["TEAM_ADMIN", "TEAM_MEMBER"]
TeamInvitationStatusValue = Literal["PENDING", "ACCEPTED", "EXPIRED", "CANCELLED"]


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=500)


class TeamPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_by_id: int
    created_at: datetime


class TeamMemberPublic(BaseModel):
    id: int
    team_id: int
    user: UserPublic
    role: TeamRoleValue
    created_at: datetime


class TeamInvitationCreateRequest(BaseModel):
    email: EmailStr
    role: TeamRoleValue = "TEAM_MEMBER"


class TeamInvitationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    email: EmailStr
    role: TeamRoleValue
    status: TeamInvitationStatusValue
    invited_by_id: int
    accepted_by_id: int | None
    expires_at: datetime
    accepted_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime


class TeamMemberRoleUpdateRequest(BaseModel):
    role: TeamRoleValue


class ActionResponse(BaseModel):
    status: str
