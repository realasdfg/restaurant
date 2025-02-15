from datetime import datetime, timedelta

from sqlalchemy import select, func, case, cast, Date

from app.database import async_session
from app.models.enums import MenuItemTypeEnum
from app.models.orders import Order, OrderItem
from app.repositories.repository import SQLAlchemyRepository


class OrderItemsRepository(SQLAlchemyRepository):
    model = OrderItem


class OrdersRepository(SQLAlchemyRepository):
    model = Order

    def _get_revenue_and_cost_expr(self):
        """Створює вирази для підрахунку доходу та витрат"""
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

    async def _aggregate_profit_query(self, start_date: datetime, end_date: datetime, group_by_date=False):
        """Формує запит для підрахунку доходу, витрат і прибутку з можливістю групування за датами."""
        revenue_expr, cost_expr = self._get_revenue_and_cost_expr()

        stmt = select(
            *([cast(self.model.created_at, Date).label("date")] if group_by_date else []),
            func.coalesce(func.sum(revenue_expr), 0).label("total_revenue"),
            func.coalesce(func.sum(cost_expr), 0).label("total_cost"),
            func.coalesce(func.sum(revenue_expr) - func.sum(cost_expr), 0).label("total_profit")
        ).select_from(self.model) \
            .join(OrderItem, OrderItem.order_id == Order.id) \
            .filter(self.model.paid == True) \
            .filter(self.model.created_at >= start_date) \
            .filter(self.model.created_at <= end_date)

        if group_by_date:
            stmt = stmt.group_by("date").order_by("date")

        async with async_session() as session:
            result = await session.execute(stmt)

        return result.all() if group_by_date else result.mappings().first()

    async def get_total_profit(self, start_date: datetime, end_date: datetime):
        """Повертає загальний дохід, витрати і прибуток за період"""
        return await self._aggregate_profit_query(start_date, end_date) or {
            "total_revenue": 0, "total_cost": 0, "total_profit": 0
        }

    async def get_daily_profit(self, start_date: datetime, end_date: datetime):
        """Повертає список прибутків по днях за вказаний період"""
        result = await self._aggregate_profit_query(start_date, end_date, group_by_date=True)

        revenue_data = {row.date: {"total_revenue": row.total_revenue, "total_cost": row.total_cost,
                                   "total_profit": row.total_profit} for row in result}

        full_dates = [start_date.date() + timedelta(days=i) for i in range((end_date.date() - start_date.date()).days + 1)]

        return [{"date": date, **revenue_data.get(date, {"total_revenue": 0, "total_cost": 0, "total_profit": 0})}
                for date in full_dates]