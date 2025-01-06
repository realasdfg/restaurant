from datetime import datetime

from sqlalchemy import ForeignKey, String, DECIMAL, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from decimal import Decimal

from app.database import Base


class Table(Base):
    __tablename__ = 'tables'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    orders: Mapped[list['Order']] = relationship(
        'Order', back_populates='table', cascade='all, delete-orphan'
    )

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(Enum('dinein', 'togo', name='order_type'))
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    paid: Mapped[bool] = mapped_column(default=False)
    paid_at: Mapped[datetime | None] = mapped_column()
    paid_by_card: Mapped[Decimal] = mapped_column(DECIMAL(7, 2), default=0)
    paid_by_cash: Mapped[Decimal] = mapped_column(DECIMAL(7, 2), default=0)
    table_id: Mapped[int | None] = mapped_column(ForeignKey('tables.id'))


    table: Mapped['Table'] = relationship('Table', back_populates='orders')


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey('menu_items.id'))
    quantity: Mapped[int] = mapped_column()
