from fastapi import Depends, HTTPException
from starlette import status

from app.dependencies import users_service
from app.models.users import User
from app.schemas.users import RoleEnum
from app.services.users import UsersService
from app.utils.auth import oauth2_scheme, verify_token

ROLE_HIERARCHY = {
    RoleEnum.STAFF: 1,
    RoleEnum.ADMIN: 2,
}


async def has_access(user_role: RoleEnum, required_role: RoleEnum) -> bool:
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]


async def get_current_user(user_service: UsersService = Depends(users_service), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = await verify_token(token, token_type='access')
    user_username: str = payload.get("sub")
    user = (await user_service.get_users({'username': user_username}))[0]
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_or_none(user_service: UsersService = Depends(users_service),
                                   token: str | None = Depends(oauth2_scheme)):
    if token is None:
        return None
    try:
        payload = await verify_token(token, token_type='access')
        user_username: str = payload.get("sub")
        user = (await user_service.get_users({'username': user_username}))[0]
        return user
    except HTTPException:
        return None


def get_current_user_if_role(required_role: RoleEnum):
    async def role_checker(user: User = Depends(get_current_user)):
        user_role = user.role
        if not await has_access(user_role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role {user_role.name}",
            )
        return user

    return role_checker


def get_current_user_if_role_or_none(required_role: RoleEnum):
    async def role_checker(user: User | None = Depends(get_current_user_or_none)):
        if user is None:
            return None
        user_role = user.role
        if not await has_access(user_role, required_role):
            return None
        return user

    return role_checker
