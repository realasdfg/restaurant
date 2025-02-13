from app.models.orders import Order, OrderItem
from app.repositories.repository import SQLAlchemyRepository


class OrdersRepository(SQLAlchemyRepository):
    model = Order


class OrderItemsRepository(SQLAlchemyRepository):
    model = OrderItem
