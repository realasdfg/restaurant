from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import RoleEnum


class SBaseUser(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    first_name: str = Field(min_length=1, max_length=30)
    last_name: str = Field(min_length=1, max_length=30)
    role: RoleEnum = RoleEnum.STAFF

    class Config:
        extra = 'forbid'


class SUserAdd(SBaseUser):
    password: str = Field(min_length=8)


class SUser(SBaseUser):
    id: int
    created_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True


class SUserEdit(SUserAdd):
    username: str | None = Field(None, min_length=3, max_length=30)
    first_name: str | None = Field(None, min_length=1, max_length=30)
    last_name: str | None = Field(None, min_length=1, max_length=30)
    role: RoleEnum | None = None
    password: str | None = Field(None, min_length=8)
