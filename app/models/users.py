from datetime import datetime

from sqlalchemy import String, func, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.schemas.users import RoleEnum


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str]
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
