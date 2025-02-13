from app.models.orders import Order
from app.repositories.repository import SQLAlchemyRepository


class OrdersRepository(SQLAlchemyRepository):
    model = Order
