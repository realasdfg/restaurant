from fastapi import HTTPException

from app.models.menu import MenuCategory, MenuItem
from app.models.users import User
from app.schemas.menu import SMenuCategoryAdd, SMenuItemAdd, SMenuItemEdit, SMenuItemFilter
from app.services.crud_base import BaseCRUDService


class MenuCategoriesService(BaseCRUDService):

    async def add_menu_category(self, menu_category_data: SMenuCategoryAdd) -> MenuCategory:
        category_dict = menu_category_data.model_dump()
        return await self._create(category_dict)

    async def get_menu_categories(self) -> list[MenuCategory]:
        return await self._get_all()

    async def get_menu_category_by_id(self, category_id) -> MenuCategory | None:
        return await self._get_one({'id': category_id})

    async def update_menu_category_by_id(self, category_id: int, menu_category_data: SMenuCategoryAdd) -> MenuCategory:
        edit_category_dict = menu_category_data.model_dump()
        updated_category = await self._update(category_id, edit_category_dict)
        if not updated_category:
            raise ValueError("Category not found")
        return updated_category

    async def delete_menu_category_by_id(self, category_id: int, item_service: 'MenuItemsService') -> MenuCategory:
        menu_items = await item_service._get_all({'category_id': category_id})
        if menu_items:
            raise HTTPException(status_code=400, detail="Cannot delete category with items")
        deleted_category = await self._delete(category_id)
        if not deleted_category:
            raise ValueError("Category not found")
        return deleted_category


class MenuItemsService(BaseCRUDService):

    async def add_menu_item(self, menu_item: SMenuItemAdd, category_service: MenuCategoriesService) -> MenuItem:
        category = await category_service.get_menu_category_by_id(menu_item.category_id)
        if not category:
            raise ValueError("Category not found")

        item_dict = menu_item.model_dump()
        return await self._create(item_dict)

    async def get_menu_items(self, filters: SMenuItemFilter, admin_user: User | None = None) -> list[MenuItem]:
        if admin_user is None:
            if filters.available is False:
                raise HTTPException(status_code=403, detail="Forbidden")
            filters.available = True
        filters_dict = filters.model_dump(exclude_none=True)
        return await self._get_all(filters_dict)

    async def get_menu_item_by_id(self, item_id) -> MenuItem | None:
        return await self._get_one({'id': item_id})

    async def update_menu_item_by_id(self, item_id, edit_menu_item_data: SMenuItemEdit,
                                     category_service: MenuCategoriesService) -> MenuItem:
        if edit_menu_item_data.category_id is not None:
            category = await category_service.get_menu_category_by_id(edit_menu_item_data.category_id)
            if not category:
                raise ValueError("Category not found")
        edit_item_dict = edit_menu_item_data.model_dump(exclude_unset=True)
        updated_item = await self._update(item_id, edit_item_dict)
        if not updated_item:
            raise ValueError("Menu item not found")
        return updated_item

    async def delete_menu_item_by_id(self, item_id) -> MenuItem:
        deleted_item = await self._delete(item_id)
        if deleted_item is None:
            raise ValueError("Menu item not found")
        return deleted_item
