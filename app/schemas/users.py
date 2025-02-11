import enum
from datetime import datetime

from pydantic import BaseModel, Field


class RoleEnum(enum.Enum):
    STAFF = "staff"
    ADMIN = "admin"


class SBaseUser(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    role: RoleEnum = RoleEnum.STAFF


class SUser(SBaseUser):
    id: int
    created_at: datetime
    is_deleted: bool = False


class SUserEdit(SBaseUser):
    username: str | None = Field(None, min_length=3, max_length=50)
    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    role: RoleEnum | None = None
