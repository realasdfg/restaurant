from fastapi import Depends, HTTPException
from starlette import status

from app.models.users import User
from app.schemas.users import RoleEnum
from app.services.auth import get_current_user, get_current_user_or_none

ROLE_HIERARCHY = {
    RoleEnum.STAFF: 1,
    RoleEnum.ADMIN: 2,
}

async def has_access(user_role: RoleEnum, required_role: RoleEnum) -> bool:
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]

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
