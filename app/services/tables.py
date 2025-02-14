from fastapi import HTTPException

from app.models.orders import OrderItem
from app.models.tables import Table
from app.schemas.tables import STableAdd
from app.services.crud_base import BaseCRUDService
from app.services.orders import OrderItemsService


class TablesService(BaseCRUDService):

    async def add_table(self, table_data: STableAdd) -> Table:
        table_dict = table_data.model_dump()
        return await self.create(table_dict)

    async def get_tables(self) -> list[Table]:
        return await self.get_all()

    async def get_table_by_id(self, table_id) -> Table | None:
        return await self.get_one({'id': table_id})

    async def update_table_by_id(self, table_id: int, edit_table_data: STableAdd) -> Table:
        edit_table_dict = edit_table_data.model_dump()
        updated_table = await self.update(table_id, edit_table_dict)
        if not updated_table:
            raise ValueError("Table not found")
        return updated_table

    async def delete_table_by_id(self, table_id: int) -> Table:
        table = await self.get_table_by_id(table_id)
        if not table:
            raise ValueError("Table not found")
        if not table.is_free:
            raise HTTPException(status_code=400, detail="Cannot delete occupied table")
        return await self.delete(table_id)

    async def set_is_free(self, table_id: int, is_free: bool) -> Table:
        table = await self.get_table_by_id(table_id)
        if not table:
            raise ValueError("Table not found")
        return await self.update(table_id, {'is_free': is_free})
