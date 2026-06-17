from app.repositories.menu import MenuCategoriesRepository, MenuItemsRepository
from app.repositories.orders import OrdersRepository, OrderItemsRepository
from app.repositories.tables import TablesRepository
from app.repositories.users import UsersRepository
from app.services.auth import AuthService
from app.services.menu import MenuCategoriesService, MenuItemsService
from app.services.orders import OrdersService, OrderItemsService
from app.services.tables import TablesService
from app.services.users import UsersService


def menu_categories_service():
    return MenuCategoriesService(MenuCategoriesRepository)


def menu_items_service():
    return MenuItemsService(MenuItemsRepository)


def users_service():
    return UsersService(UsersRepository)


def auth_service():
    return AuthService(UsersRepository)


def tables_service():
    return TablesService(TablesRepository)


def orders_service():
    return OrdersService(OrdersRepository)


def order_items_service():
    return OrderItemsService(OrderItemsRepository)
