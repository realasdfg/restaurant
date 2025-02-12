from app.repositories.menu import MenuCategoriesRepository, MenuItemsRepository
from app.services.menu import MenuCategoriesService, MenuItemsService


def menu_categories_service():
    return MenuCategoriesService(MenuCategoriesRepository)


def menu_items_service():
    return MenuItemsService(MenuItemsRepository)
