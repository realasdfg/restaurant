from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.dependencies import users_service
from app.models.users import User
from app.schemas.users import SUser, SUserEdit, SUserAdd
from app.models.enums import RoleEnum
from app.services.users import UsersService
from app.utils.users import get_current_user_if_role, get_current_user

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('')
async def add_user(user_data: SUserAdd, user_service: UsersService = Depends(users_service),
                   current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
    try:
        new_user = await user_service.add_user(user_data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User with this username already exists")
    return SUser.model_validate(new_user)


@router.get('')
async def get_all_users(user_service: UsersService = Depends(users_service),
                        current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> list[SUser]:
    users = await user_service.get_users()
    return [SUser.model_validate(user) for user in users]


@router.get('/me')
async def get_me(current_user: User = Depends(get_current_user)) -> SUser:
    return SUser.model_validate(current_user)


@router.get('/{user_id}')
async def get_user(user_id: int, user_service: UsersService = Depends(users_service),
                   current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return SUser.model_validate(user)


@router.patch('/{user_id}')
async def update_user(user_id: int, user_data: SUserEdit,
                      user_service: UsersService = Depends(users_service),
                      current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
    try:
        user = await user_service.update_user_by_id(user_id, user_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User with this username already exists")
    return SUser.model_validate(user)


@router.delete('/{user_id}')
async def delete_user(user_id: int,
                      user_service: UsersService = Depends(users_service),
                      current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
    try:
        await user_service.delete_user_by_id(user_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": 200, "message": f"User with id {user_id} deleted"}
