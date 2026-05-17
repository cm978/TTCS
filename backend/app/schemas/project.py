from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.auth import UserPublic

ProjectRoleValue = Literal["PROJECT_MANAGER", "PROJECT_MEMBER"]
BoardColumnStatusValue = Literal["TODO", "IN_PROGRESS", "IN_REVIEW", "REJECTED", "DONE"]


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_order(self) -> "ProjectCreateRequest":
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("Project end date must be later than start date")
        return self


class ProjectPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    name: str
    description: str | None
    start_date: date | None
    end_date: date | None
    created_by_id: int
    created_at: datetime


class ProjectMemberPublic(BaseModel):
    id: int
    project_id: int
    user: UserPublic
    role: ProjectRoleValue
    created_at: datetime


class BoardColumnPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    status: BoardColumnStatusValue
    position: int


class ProjectBoardResponse(BaseModel):
    project: ProjectPublic
    members: list[ProjectMemberPublic]
    columns: list[BoardColumnPublic]


class ProjectMemberAddRequest(BaseModel):
    user_id: int
    role: ProjectRoleValue = "PROJECT_MEMBER"


class ProjectMemberRoleUpdateRequest(BaseModel):
    role: ProjectRoleValue
