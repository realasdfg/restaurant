from sqlalchemy import String, Index, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.orders import Order


class Table(Base):
    __tablename__ = 'tables'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    is_free: Mapped[bool] = mapped_column(default=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    orders: Mapped[list['Order']] = relationship(
        'Order', back_populates='table', cascade='all, delete-orphan', lazy="selectin"
    )

    __table_args__ = (
        Index('unique_table_name', 'name', unique=True, postgresql_where=(text("is_deleted = FALSE"))),
        CheckConstraint("LENGTH(name) >= 1", name="tables_check_name_length"),
    )
