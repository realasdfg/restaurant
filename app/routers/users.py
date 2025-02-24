from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.dependencies import users_service
from app.models.users import User
from app.schemas.users import SUser, SUserEdit, SUserAdd
from app.models.enums import RoleEnum
from app.services.users import UsersService
from app.utils.users import get_current_user_if_role, get_current_user


class UsersRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/users", tags=["Users"])
        self.router.add_api_route("", self.add_user, methods=["POST"])
        self.router.add_api_route("", self.get_all_users, methods=["GET"])
        self.router.add_api_route("/me", self.get_me, methods=["GET"])
        self.router.add_api_route("/{user_id}", self.get_user, methods=["GET"])
        self.router.add_api_route("/{user_id}", self.update_user, methods=["PATCH"])
        self.router.add_api_route("/{user_id}", self.delete_user, methods=["DELETE"])

    async def add_user(self, user_data: SUserAdd, user_service: UsersService = Depends(users_service),
                       current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
        try:
            new_user = await user_service.add_user(user_data)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="User with this username already exists")
        return SUser.model_validate(new_user)

    async def get_all_users(self, user_service: UsersService = Depends(users_service), include_deleted: bool = False,
                            current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> list[SUser]:
        users = await user_service.get_users(include_deleted=include_deleted)
        return [SUser.model_validate(user) for user in users]

    async def get_me(self, current_user: User = Depends(get_current_user)) -> SUser:
        return SUser.model_validate(current_user)

    async def get_user(self, user_id: int, user_service: UsersService = Depends(users_service),
                       include_deleted: bool = False,
                       current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
        user = await user_service.get_user_by_id(user_id, include_deleted)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return SUser.model_validate(user)

    async def update_user(self, user_id: int, user_data: SUserEdit,
                          user_service: UsersService = Depends(users_service),
                          current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SUser:
        try:
            user = await user_service.update_user_by_id(user_id, user_data, current_user)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except IntegrityError:
            raise HTTPException(status_code=400, detail="User with this username already exists")
        return SUser.model_validate(user)

    async def delete_user(self, user_id: int, user_service: UsersService = Depends(users_service),
                          current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
        try:
            await user_service.delete_user_by_id(user_id, current_user)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {"status": 200, "detail": f"User with id {user_id} deleted"}
