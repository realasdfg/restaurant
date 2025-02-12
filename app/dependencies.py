from app.repositories.menu import MenuCategoriesRepository, MenuItemsRepository
from app.repositories.users import UsersRepository
from app.services.auth import AuthService
from app.services.menu import MenuCategoriesService, MenuItemsService
from app.services.users import UsersService


def menu_categories_service():
    return MenuCategoriesService(MenuCategoriesRepository)


def menu_items_service():
    return MenuItemsService(MenuItemsRepository)


def users_service():
    return UsersService(UsersRepository)


def auth_service():
    return AuthService(UsersRepository)
