from app.repositories.menu import MenuCategoriesRepository, MenuItemsRepository
from app.services.menu import MenuCategoriesService, MenuItemsService


def menu_category_service():
    return MenuCategoriesService(MenuCategoriesRepository)


def menu_item_service():
    return MenuItemsService(MenuItemsRepository)
