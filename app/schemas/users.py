import enum
from datetime import datetime

from pydantic import BaseModel, Field


class RoleEnum(enum.Enum):
    WORKER = "worker"
    ADMIN = "admin"
    OWNER = "owner"


class SUser(BaseModel):
    username: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    role: RoleEnum = RoleEnum.WORKER


class SUserResponse(SUser):
    id: int
    created_at: datetime
