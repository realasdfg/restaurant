from app.models.tables import Table
from app.repositories.repository import SQLAlchemyRepository


class TablesRepository(SQLAlchemyRepository):
    model = Table
    soft_delete_field = 'is_deleted'
