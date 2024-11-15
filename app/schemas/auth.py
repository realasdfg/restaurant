from pydantic import Field, BaseModel

from app.schemas.users import SUser, SUserResponse


class SUserRegister(SUser):
    password: str = Field(min_length=8)


class SUserLogin(BaseModel):
    username: str
    password: str


class SToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class SUserLoginResponse(SToken, SUserResponse):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
