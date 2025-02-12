from app.models.users import User
from app.repositories.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User
    soft_delete_field = 'is_deleted'
