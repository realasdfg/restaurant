import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings
from app.models.menu import MenuCategory, MenuItem
from app.models.users import User
from app.schemas.menu import SMenuCategoryAdd, SMenuItemAdd, SMenuItemEdit, SMenuItemFilter
from app.services.crud_base import BaseCRUDService


class MenuCategoriesService(BaseCRUDService):

    async def add_menu_category(self, menu_category_data: SMenuCategoryAdd) -> MenuCategory:
        category_dict = menu_category_data.model_dump()
        return await self.create(category_dict)

    async def get_menu_categories(self, include_deleted: bool = False) -> list[MenuCategory]:
        return await self.get_all(order_by=MenuCategory.id, include_deleted=include_deleted)

    async def get_menu_category_by_id(self, category_id, include_deleted: bool = False) -> MenuCategory | None:
        return await self.get_one({'id': category_id}, include_deleted)

    async def update_menu_category_by_id(self, category_id: int, menu_category_data: SMenuCategoryAdd) -> MenuCategory:
        edit_category_dict = menu_category_data.model_dump()
        updated_category = await self.update(category_id, edit_category_dict)
        if not updated_category:
            raise ValueError("Category not found")
        return updated_category

    async def delete_menu_category_by_id(self, category_id: int, item_service: 'MenuItemsService') -> MenuCategory:
        menu_items = await item_service.get_all({'category_id': category_id})
        if menu_items:
            raise HTTPException(status_code=400, detail="Cannot delete category with items")
        deleted_category = await self.delete(category_id)
        if not deleted_category:
            raise ValueError("Category not found")
        return deleted_category


class MenuItemsService(BaseCRUDService):
    async def add_menu_item(self, menu_item_data: SMenuItemAdd, image: UploadFile,
                            category_service: MenuCategoriesService) -> MenuItem:
        category = await category_service.get_menu_category_by_id(menu_item_data.category_id)
        if not category:
            raise ValueError("Category not found")

        unique_name = await self._write_image(image)

        item_dict = menu_item_data.model_dump()
        item_dict['image'] = f"images/{unique_name}"
        return await self.create(item_dict)

    async def get_menu_items(self, filters: SMenuItemFilter, admin_user: User | None = None,
                             include_deleted: bool = False) -> list[MenuItem]:
        if admin_user is None:
            if filters.available is False:
                raise HTTPException(status_code=403, detail="Forbidden")
            filters.available = True
        filters_dict = filters.model_dump(exclude_none=True)
        return await self.get_all(filters_dict, order_by=MenuItem.id, include_deleted=include_deleted)

    async def get_menu_item_by_id(self, item_id, include_deleted: bool = False) -> MenuItem | None:
        return await self.get_one({'id': item_id}, include_deleted)

    async def update_menu_item_by_id(self, item_id, category_service: MenuCategoriesService,
                                     edit_menu_item_data: SMenuItemEdit | None = None,
                                     image: UploadFile | None = None) -> MenuItem:
        edit_item_dict = {}
        if edit_menu_item_data is not None:
            if edit_menu_item_data.category_id is not None:
                category = await category_service.get_menu_category_by_id(edit_menu_item_data.category_id)
                if not category:
                    raise ValueError("Category not found")
            edit_item_dict = edit_menu_item_data.model_dump(exclude_unset=True)
        if image is not None:
            unique_name = await self._write_image(image)
            edit_item_dict['image'] = f"images/{unique_name}"

        updated_item = await self.update(item_id, edit_item_dict)
        if not updated_item:
            raise ValueError("Menu item not found")
        return updated_item

    async def delete_menu_item_by_id(self, item_id) -> MenuItem:
        deleted_item = await self.delete(item_id)
        if deleted_item is None:
            raise ValueError("Menu item not found")
        return deleted_item

    async def _write_image(self, image):
        ext = image.filename.split(".")[-1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = Path(settings.file_upload_dir) / unique_name
        with open(file_path, "wb") as f:
            f.write(await image.read())
        return unique_name
