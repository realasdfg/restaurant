from pydantic import Field, BaseModel

from app.schemas.users import SBaseUser, SUserResponse


class SUserRegister(SBaseUser):
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
