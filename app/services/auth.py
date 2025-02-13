from fastapi import HTTPException
from starlette import status

from app.models.users import User
from app.schemas.auth import SUserLogin
from app.services.crud_base import BaseCRUDService
from app.utils.auth import verify_password


class AuthService(BaseCRUDService):

    async def authenticate_user(self, user_login_data: SUserLogin) -> User:
        user = await self._get_one({'username': user_login_data.username})
        if not user or not verify_password(user_login_data.password, user.password):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invalid username or password")
        return user
