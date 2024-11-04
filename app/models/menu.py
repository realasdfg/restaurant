from sqlalchemy import ForeignKey, String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from decimal import Decimal

from app.database import Base


class MenuCategory(Base):
    __tablename__ = 'menu_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    items: Mapped[list['MenuItem']] = relationship(
        'MenuItem', back_populates='category', cascade='all, delete-orphan'
    )


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column()
    image: Mapped[str | None] = mapped_column()
    price: Mapped[Decimal] = mapped_column(DECIMAL(7, 2))
    cost: Mapped[Decimal] = mapped_column(DECIMAL(7, 2))
    available: Mapped[bool] = mapped_column()
    category_id: Mapped[int] = mapped_column(ForeignKey('menu_categories.id'))

    category: Mapped['MenuCategory'] = relationship('MenuCategory', back_populates='items')
