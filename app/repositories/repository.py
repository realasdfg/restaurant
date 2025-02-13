from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete

from app.database import async_session


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, filters: dict, include_deleted: bool = False):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, filters: dict = None, include_deleted: bool = False):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, filters: dict, update_data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, filters: dict):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None
    soft_delete_field = None  # ex. 'is_deleted'

    async def add_one(self, data: dict):
        async with async_session() as session:
            stmt = insert(self.model).values(**data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def find_one(self, filters: dict, include_deleted: bool = False):
        async with async_session() as session:
            if self.soft_delete_field and not include_deleted:
                filters = filters or {}
                filters[self.soft_delete_field] = False

            stmt = select(self.model).filter_by(**filters)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_all(self, filters: dict = None, include_deleted: bool = False):
        async with async_session() as session:
            if self.soft_delete_field and not include_deleted:
                filters = filters or {}
                filters[self.soft_delete_field] = False

            stmt = select(self.model)
            conditions = self._build_conditions(filters)
            if conditions:
                stmt = stmt.filter(*conditions)

            res = await session.execute(stmt)
            return res.scalars().all()

    async def update_one(self, filters: dict, update_data: dict):
        async with async_session() as session:
            if self.soft_delete_field:
                filters[self.soft_delete_field] = False

            stmt = (update(self.model)
                    .where(*[getattr(self.model, key) == value for key, value in filters.items()])
                    .values(**update_data)
                    .returning(self.model))
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one_or_none()

    async def delete_one(self, filters: dict):
        async with async_session() as session:
            if self.soft_delete_field:
                filters[self.soft_delete_field] = False
                update_data = {self.soft_delete_field: True}
                stmt = (update(self.model)
                        .where(*[getattr(self.model, key) == value for key, value in filters.items()])
                        .values(**update_data)
                        .returning(self.model))
            else:
                stmt = (delete(self.model)
                        .where(*[getattr(self.model, key) == value for key, value in filters.items()])
                        .returning(self.model))

            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one_or_none()

    def _build_conditions(self, filters: dict):
        conditions = []
        for key, value in filters.items():
            if isinstance(key, tuple):
                column, operator = key
                if operator == ">=":
                    conditions.append(column >= value)
                elif operator == "<=":
                    conditions.append(column <= value)
                elif operator == "!=":
                    conditions.append(column != value)
                else:
                    raise ValueError(f"Unsupported operator: {operator}")
            else:
                conditions.append(getattr(self.model, key) == value)
        return conditions
