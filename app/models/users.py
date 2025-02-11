from datetime import datetime

from sqlalchemy import String, func, Enum as SqlEnum, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.schemas.users import RoleEnum


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[str]
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        Index('unique_user_username', 'username', unique=True, postgresql_where=(text("is_deleted = FALSE"))),
    )