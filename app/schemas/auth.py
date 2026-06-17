from pydantic import BaseModel

from app.schemas.users import SUser


class SUserLogin(BaseModel):
    username: str
    password: str


class SToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class SUserLoginResponse(SToken, SUser):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
