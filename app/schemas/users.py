import enum
from datetime import datetime

from pydantic import BaseModel, Field


class RoleEnum(enum.Enum):
    STAFF = "staff"
    ADMIN = "admin"


class SBaseUser(BaseModel):
    username: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    role: RoleEnum = RoleEnum.STAFF


class SUser(BaseModel):
    created_at: datetime
    is_deleted: bool = False


class SUserResponse(SUser):
    id: int


class SUserEdit(SUser):
    username: str | None = Field(None, max_length=50)
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    role: RoleEnum | None = None
