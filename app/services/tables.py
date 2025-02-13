from app.schemas.tables import STableAdd
from app.services.crud_base import BaseCRUDService


class TablesService(BaseCRUDService):

    async def add_table(self, table_data: STableAdd):
        table_dict = table_data.model_dump()
        return await self._create(table_dict)

    async def get_tables(self):
        return await self._get_all()

    async def get_table_by_id(self, table_id):
        return await self._get_one({'id': table_id})

    async def update_table_by_id(self, table_id: int, edit_table_data: STableAdd):
        edit_table_dict = edit_table_data.model_dump()
        updated_table = await self._update(table_id, edit_table_dict)
        if not updated_table:
            raise ValueError("Table not found")
        return updated_table

    async def delete_table_by_id(self, table_id: int):
        deleted_table = await self._delete(table_id)
        if not deleted_table:
            raise ValueError("Table not found")
        return deleted_table

    async def toggle_is_free(self, table_id: int):
        table = await self.get_table_by_id(table_id)
        if not table:
            raise ValueError("Table not found")
        new_value = not table.is_free
        return await self._update(table_id, {'is_free': new_value})
