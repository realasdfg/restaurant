from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.users import User
from app.schemas.users import RoleEnum, SUser, SUserEdit
from app.utils.auth import get_current_user
from app.utils.roles import get_current_user_if_role

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('')
async def get_all_users(session: AsyncSession = Depends(get_async_session),
                        current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> list[SUser]:
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [SUser.model_validate(user, from_attributes=True) for user in users]


@router.get('/me')
async def get_me(current_user: User = Depends(get_current_user)) -> SUser:
    return SUser.model_validate(current_user, from_attributes=True)


@router.get('/{user_id}')
async def get_user(user_id: int,
                   session: AsyncSession = Depends(get_async_session),
                   current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return SUser.model_validate(user, from_attributes=True)


@router.patch('/{user_id}')
async def update_user(user_id: int,
                      user_data: SUserEdit,
                      session: AsyncSession = Depends(get_async_session),
                      current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_data.role:
        if user == current_user and current_user.role == RoleEnum.ADMIN:
            raise HTTPException(status_code=403, detail="Admin cannot change their own role")
        else:
            user.role = user_data.role
    if user_data.username:
        user.username = user_data.username
    if user_data.first_name:
        user.first_name = user_data.first_name
    if user_data.last_name:
        user.last_name = user_data.last_name
    await session.commit()
    return SUser.model_validate(user, from_attributes=True)


@router.delete('/{user_id}')
async def delete_user(user_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(status_code=403, detail="Admin cannot delete himself")
    await session.delete(user)
    await session.commit()
    return {"status": 200, "message": "User deleted"}
