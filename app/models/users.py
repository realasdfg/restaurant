from datetime import datetime

from sqlalchemy import String, func, Enum as SqlEnum, Index, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import RoleEnum


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str]
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        Index('unique_user_username', 'username', unique=True, postgresql_where=(text("is_deleted = FALSE"))),
        CheckConstraint("LENGTH(username) >= 3", name="users_check_username_length"),
        CheckConstraint("LENGTH(first_name) >= 1", name="users_check_first_name_length"),
        CheckConstraint("LENGTH(last_name) >= 1", name="users_check_last_name_length"),
    )