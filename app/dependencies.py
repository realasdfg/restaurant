from app.repositories.menu import MenuCategoriesRepository, MenuItemsRepository
from app.repositories.users import UsersRepository
from app.services.menu import MenuCategoriesService, MenuItemsService
from app.services.users import UsersService


def menu_categories_service():
    return MenuCategoriesService(MenuCategoriesRepository)


def menu_items_service():
    return MenuItemsService(MenuItemsRepository)


def users_service():
    return UsersService(UsersRepository)
