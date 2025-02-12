from sqlalchemy import ForeignKey, String, DECIMAL, Enum as SqlEnum, Index, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from decimal import Decimal

from app.database import Base
from app.models.orders import OrderItem
from app.schemas.menu import MenuItemTypeEnum


class MenuCategory(Base):
    __tablename__ = 'menu_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    is_deleted: Mapped[bool] = mapped_column(default=False)

    items: Mapped[list['MenuItem']] = relationship(
        'MenuItem', back_populates='category', cascade='all, delete-orphan', lazy="selectin"
    )

    __table_args__ = (
        Index('unique_menu_category_name', 'name', unique=True, postgresql_where=(text("is_deleted = FALSE"))),
        CheckConstraint("LENGTH(name) >= 1", name="menu_categories_check_name_length"),
    )


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column()
    image: Mapped[str | None] = mapped_column()
    price: Mapped[Decimal] = mapped_column(DECIMAL(7, 2))
    cost: Mapped[Decimal] = mapped_column(DECIMAL(7, 2))
    type: Mapped[MenuItemTypeEnum] = mapped_column(SqlEnum(MenuItemTypeEnum))
    weight: Mapped[int] = mapped_column()
    available: Mapped[bool] = mapped_column(default=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('menu_categories.id'))
    is_deleted: Mapped[bool] = mapped_column(default=False)

    category: Mapped['MenuCategory'] = relationship('MenuCategory', back_populates='items', lazy="selectin")
    order_items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='menu_item', lazy="selectin")

    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 1", name="menu_items_check_name_length"),
        CheckConstraint("price >= 0", name="menu_items_check_price_non_negative"),
        CheckConstraint("cost >= 0", name="menu_items_check_cost_non_negative"),
    )