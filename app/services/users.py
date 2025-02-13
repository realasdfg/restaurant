from fastapi import HTTPException

from app.models.users import User
from app.schemas.users import SUserAdd, SUserEdit
from app.services.crud_base import BaseCRUDService
from app.utils.auth import get_password_hash


class UsersService(BaseCRUDService):

    async def add_user(self, user: SUserAdd) -> User:
        hashed_password = get_password_hash(user.password)
        user_dict = user.model_dump()
        user_dict['password'] = hashed_password
        return await self._create(user_dict)

    async def get_users(self, filters: dict = None) -> list[User]:
        return await self._get_all(filters)

    async def get_user_by_id(self, user_id) -> User | None:
        return await self._get_one({'id': user_id})

    async def update_user_by_id(self, user_id: int, edit_user_data: SUserEdit, current_user: User) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if edit_user_data.role and user.id == current_user.id:
            raise HTTPException(status_code=403, detail="Admin cannot change his own role")

        edit_user_dict = edit_user_data.model_dump(exclude_unset=True)
        return await self._update(user_id, edit_user_dict)

    async def delete_user_by_id(self, user_id, current_user: User) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if user.id == current_user.id:
            raise HTTPException(status_code=403, detail="Admin cannot delete himself")

        return await self._delete(user_id)
