import enum
from datetime import datetime

from pydantic import BaseModel, Field


class RoleEnum(enum.Enum):
    STAFF = "staff"
    ADMIN = "admin"


class SUser(BaseModel):
    username: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    role: RoleEnum = RoleEnum.STAFF


class SUserResponse(SUser):
    id: int
    created_at: datetime
