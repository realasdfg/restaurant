from datetime import datetime, timedelta

from sqlalchemy import select, func, case, cast, Date

from app.database import async_session
from app.models.enums import MenuItemTypeEnum
from app.models.menu import MenuItem
from app.models.orders import Order, OrderItem
from app.repositories.repository import SQLAlchemyRepository
from app.schemas.statistics import SOrdersRevenue


class OrderItemsRepository(SQLAlchemyRepository):
    model = OrderItem


class OrdersRepository(SQLAlchemyRepository):
    model = Order

    @staticmethod
    def _get_revenue_and_cost_expr():
        """Створює вирази для підрахунку доходу та витрат по OrderItem."""
        revenue_expr = case(
            (OrderItem.type == MenuItemTypeEnum.BY_QUANTITY,
             OrderItem.price * OrderItem.quantity),
            (OrderItem.type == MenuItemTypeEnum.BY_WEIGHT,
             (OrderItem.price / OrderItem.weight) * OrderItem.quantity),
            else_=0
        )

        cost_expr = case(
            (OrderItem.type == MenuItemTypeEnum.BY_QUANTITY,
             OrderItem.cost * OrderItem.quantity),
            (OrderItem.type == MenuItemTypeEnum.BY_WEIGHT,
             (OrderItem.cost / OrderItem.weight) * OrderItem.quantity),
            else_=0
        )

        return revenue_expr, cost_expr

    async def _aggregate_profit_query(self, filters: SOrdersRevenue, group_by_date=False):
        """
        Формує запит для підрахунку:
         - total_revenue: сумарного доходу за OrderItem,
         - total_cost: сумарних витрат за OrderItem,
         - total_profit: різниці між доходом та витратами.

        Якщо filters.category_id заданий, враховуються лише OrderItem, у яких
        відповідний MenuItem має задане category_id.
        """
        revenue_expr, cost_expr = self._get_revenue_and_cost_expr()

        stmt = select(
            *([cast(self.model.created_at, Date).label("date")] if group_by_date else []),
            func.coalesce(func.sum(revenue_expr), 0).label("total_revenue"),
            func.coalesce(func.sum(cost_expr), 0).label("total_cost"),
            func.coalesce(func.sum(revenue_expr) - func.sum(cost_expr), 0).label("total_profit")
        ).select_from(self.model) \
            .join(OrderItem, OrderItem.order_id == Order.id) \
            .filter(self.model.paid == True) \
            .filter(self.model.created_at >= filters.from_date) \
            .filter(self.model.created_at <= filters.to_date)

        if filters.type:
            stmt = stmt.filter(self.model.type == filters.type)

        if filters.category_id:
            # Приєднуємо MenuItem через зв'язок OrderItem.menu_item та застосовуємо фільтр
            stmt = stmt.join(OrderItem.menu_item).filter(MenuItem.category_id == filters.category_id)

        if group_by_date:
            stmt = stmt.group_by("date").order_by("date")

        async with async_session() as session:
            result = await session.execute(stmt)

        return result.all() if group_by_date else result.mappings().first()

    async def get_total_profit(self, filters: SOrdersRevenue):
        """Повертає загальний total_revenue, total_cost та total_profit за період із можливістю фільтрації за категорією."""
        return await self._aggregate_profit_query(filters) or {
            "total_revenue": 0, "total_cost": 0, "total_profit": 0
        }

    async def get_daily_profit(self, filters: SOrdersRevenue):
        """Повертає список з розбивкою по днях (date, total_revenue, total_cost, total_profit) за вказаний період із фільтрацією за категорією."""
        result = await self._aggregate_profit_query(filters, group_by_date=True)

        revenue_data = {row.date: {"total_revenue": row.total_revenue,
                                   "total_cost": row.total_cost,
                                   "total_profit": row.total_profit}
                        for row in result}

        full_dates = [filters.from_date.date() + timedelta(days=i)
                      for i in range((filters.to_date.date() - filters.from_date.date()).days + 1)]

        return [
            {"date": date,
             **revenue_data.get(date, {"total_revenue": 0, "total_cost": 0, "total_profit": 0})}
            for date in full_dates
        ]