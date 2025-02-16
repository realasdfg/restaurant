from fastapi import HTTPException

from app.models.users import User
from app.schemas.users import SUserAdd, SUserEdit
from app.services.crud_base import BaseCRUDService
from app.utils.auth import get_password_hash


class UsersService(BaseCRUDService):

    async def add_user(self, user_data: SUserAdd) -> User:
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict['password'] = hashed_password
        return await self.create(user_dict)

    async def get_users(self, filters: dict = None) -> list[User]:
        return await self.get_all(filters, User.id)

    async def get_user_by_id(self, user_id) -> User | None:
        return await self.get_one({'id': user_id})

    async def update_user_by_id(self, user_id: int, edit_user_data: SUserEdit, current_user: User) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if edit_user_data.role and user.id == current_user.id:
            raise HTTPException(status_code=403, detail="Admin cannot change his own role")

        edit_user_dict = edit_user_data.model_dump(exclude_none=True)
        if edit_user_data.password:
            hashed_password = get_password_hash(edit_user_data.password)
            edit_user_dict['password'] = hashed_password

        return await self.update(user_id, edit_user_dict)

    async def delete_user_by_id(self, user_id, current_user: User) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if user.id == current_user.id:
            raise HTTPException(status_code=403, detail="Admin cannot delete himself")

        return await self.delete(user_id)
