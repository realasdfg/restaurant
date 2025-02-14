from app.repositories.repository import AbstractRepository


class BaseCRUDService:
    def __init__(self, repo_class: type[AbstractRepository]):
        self._repo = repo_class()

    async def create(self, data: dict):
        return await self._repo.add_one(data)

    async def get_all(self, filters: dict = None, order_by=None, include_deleted: bool = False):
        return await self._repo.find_all(filters=filters, order_by=order_by, include_deleted=include_deleted)

    async def get_one(self, filters: dict, include_deleted: bool = False):
        return await self._repo.find_one(filters=filters, include_deleted=include_deleted)

    async def update(self, identifier: int, update_data: dict):
        return await self._repo.update_one({'id': identifier}, update_data)

    async def delete(self, identifier: int):
        return await self._repo.delete_one({'id': identifier})
