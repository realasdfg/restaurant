from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.dependencies import auth_service
from app.services.auth import AuthService
from app.utils.auth import create_jwt_token, verify_token
from app.schemas.auth import SUserLogin, SUserLoginResponse, SToken


class AuthRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/auth", tags=["Auth"])
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/token/refresh", self.token_refresh, methods=["POST"])

    async def login(self, user_login_data: SUserLogin,
                    auth_service: AuthService = Depends(auth_service)) -> SUserLoginResponse:
        user, access_token, refresh_token = await auth_service.authenticate_user(user_login_data)
        response = SUserLoginResponse.model_validate(user)
        response.access_token = access_token
        response.refresh_token = refresh_token
        response.token_type = 'Bearer'
        return response

    async def token_refresh(self, refresh_token: str | None = None) -> SToken:
        payload = await verify_token(refresh_token, "refresh")
        user_username: str = payload.get("sub")
        if user_username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        new_access_token = await create_jwt_token(data={"sub": user_username}, token_type='access')
        new_refresh_token = await create_jwt_token(data={"sub": user_username}, token_type='refresh')
        return SToken(access_token=new_access_token, refresh_token=new_refresh_token, token_type="Bearer")
