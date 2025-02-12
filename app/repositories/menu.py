from app.models.menu import MenuCategory, MenuItem
from app.utils.repository import SQLAlchemyRepository


class MenuCategoriesRepository(SQLAlchemyRepository):
    model = MenuCategory
    soft_delete_field = 'is_deleted'

class MenuItemsRepository(SQLAlchemyRepository):
    model = MenuItem
    soft_delete_field = 'is_deleted'
