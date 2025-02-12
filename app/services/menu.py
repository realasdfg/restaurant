from fastapi import HTTPException

from app.models.users import User
from app.schemas.menu import SMenuCategoryAdd, SMenuItemAdd, SMenuItemEdit, SMenuItemFilter
from app.services.crud_base import BaseCRUDService


class MenuCategoriesService(BaseCRUDService):

    async def add_menu_category(self, menu_category: SMenuCategoryAdd):
        category_dict = menu_category.model_dump()
        return await self._create(category_dict)

    async def get_menu_categories(self):
        return await self._get_all()

    async def get_menu_category_by_id(self, category_id):
        return await self._get_one({'id': category_id})

    async def update_menu_category_by_id(self, category_id: int, edit_menu_category_data: SMenuCategoryAdd):
        edit_category_dict = edit_menu_category_data.model_dump()
        updated_category = await self._update(category_id, edit_category_dict)
        if not updated_category:
            raise ValueError("Category not found")
        return updated_category

    async def delete_menu_category_by_id(self, category_id: int):
        deleted_category = await self._delete(category_id)
        if not deleted_category:
            raise ValueError("Category not found")
        return deleted_category


class MenuItemsService(BaseCRUDService):

    async def add_menu_item(self, menu_item: SMenuItemAdd, category_service: MenuCategoriesService):
        category = await category_service.get_menu_category_by_id(menu_item.category_id)
        if not category:
            raise ValueError("Category does not exist")

        item_dict = menu_item.model_dump()
        return await self._create(item_dict)

    async def get_menu_items(self, filters: SMenuItemFilter, admin_user: User | None = None):
        if admin_user is None:
            if filters.available is False:
                raise HTTPException(status_code=403, detail="Forbidden")
            filters.available = True
        filters_dict = filters.model_dump(exclude_none=True)
        return await self._get_all(filters_dict)

    async def get_menu_item_by_id(self, item_id):
        return await self._get_one({'id': item_id})

    async def update_menu_item_by_id(self, item_id, edit_menu_item_data: SMenuItemEdit,
                                     category_service: MenuCategoriesService):
        if edit_menu_item_data.category_id is not None:
            category = await category_service.get_menu_category_by_id(edit_menu_item_data.category_id)
            if not category:
                raise ValueError("Category does not exist")
        edit_item_dict = edit_menu_item_data.model_dump(exclude_unset=True)
        updated_item = await self._update(item_id, edit_item_dict)
        if not updated_item:
            raise ValueError("Item not found")
        return updated_item

    async def delete_menu_item_by_id(self, item_id):
        deleted_item = await self._delete(item_id)
        if deleted_item is None:
            raise ValueError("Item not found")
        return deleted_item
