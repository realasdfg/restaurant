from datetime import timedelta, datetime

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

    async def _aggregate_profit_query(self, filters: SOrdersRevenue, period: str = None):
        """
        Формує запит для підрахунку:
         - total_revenue, total_cost, total_profit.

        Якщо period заданий ("daily", "weekly" або "monthly"), дані групуються за відповідним періодом.
        Фільтрування за категорією здійснюється, якщо filters.category_id заданий.
        """
        revenue_expr, cost_expr = self._get_revenue_and_cost_expr()

        # Отримуємо групувальний вираз відповідно до обраного періоду
        group_expr = None
        if period:
            period = period.lower()
            if period == "daily":
                group_expr = cast(self.model.created_at, Date)
            elif period == "weekly":
                group_expr = func.date_trunc('week', self.model.created_at)
            elif period == "monthly":
                group_expr = func.date_trunc('month', self.model.created_at)
            else:
                raise ValueError("Invalid period. Allowed values: daily, weekly, monthly.")

        stmt = select(
            *([group_expr.label("date")] if group_expr is not None else []),
            func.coalesce(func.sum(revenue_expr), 0).label("total_revenue"),
            func.coalesce(func.sum(Order.paid_by_cash), 0).label("cash_revenue"),
            func.coalesce(func.sum(Order.paid_by_card), 0).label("card_revenue"),
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
            stmt = stmt.join(OrderItem.menu_item).filter(MenuItem.category_id == filters.category_id)

        if filters.paid_online is not None:
            stmt = stmt.filter(Order.paid_online == filters.paid_online)

        if group_expr is not None:
            stmt = stmt.group_by("date").order_by("date")

        async with async_session() as session:
            result = await session.execute(stmt)

        # Для агрегованих запитів повертаємо мапінг (словники)
        return result.mappings().all() if group_expr is not None else result.mappings().first()

    async def get_total_profit(self, filters: SOrdersRevenue):
        """Повертає загальний total_revenue, total_cost та total_profit за період із можливістю фільтрації за категорією."""
        return await self._aggregate_profit_query(filters) or {
            "total_revenue": 0, "cash_revenue": 0, "card_revenue": 0,
            "total_cost": 0, "total_profit": 0
        }

    async def get_periodical_profit(self, filters: SOrdersRevenue):
        """
        Повертає список з розбивкою за періодами (daily, weekly, monthly):
         кожна група містить: date, total_revenue, cash_revenue, card_revenue, total_cost, total_profit.

        Якщо для певного періоду даних немає, повертається об’єкт із нульовими значеннями.
        """
        period = filters.period if filters.period else "daily"
        result = await self._aggregate_profit_query(filters, period=period)
        period = period.lower()

        if period == 'daily':
            # Формуємо дані для кожного дня
            revenue_data = {row['date']: {
                "total_revenue": row['total_revenue'],
                "cash_revenue": row['cash_revenue'],
                "card_revenue": row['card_revenue'],
                "total_cost": row['total_cost'],
                "total_profit": row['total_profit']
            } for row in result}
            full_dates = [filters.from_date.date() + timedelta(days=i)
                          for i in range((filters.to_date.date() - filters.from_date.date()).days + 1)]
            return [
                {"date": date,
                 **revenue_data.get(date, {"total_revenue": 0,
                                           "cash_revenue": 0,
                                           "card_revenue": 0,
                                           "total_cost": 0,
                                           "total_profit": 0})}
                for date in full_dates
            ]

        elif period == 'weekly':
            # Обчислюємо початок тижня для from_date та to_date (вважаємо, що тиждень починається з понеділка)
            start_week = filters.from_date.date() - timedelta(days=filters.from_date.date().weekday())
            end_week = filters.to_date.date() - timedelta(days=filters.to_date.date().weekday())
            full_weeks = []
            cur = start_week
            while cur <= end_week:
                full_weeks.append(cur)
                cur += timedelta(days=7)
            revenue_data = {(row['date'].date() if isinstance(row['date'], datetime) else row['date']): {
                "total_revenue": row['total_revenue'],
                "cash_revenue": row['cash_revenue'],
                "card_revenue": row['card_revenue'],
                "total_cost": row['total_cost'],
                "total_profit": row['total_profit']
            } for row in result}
            return [
                {"date": week,
                 **revenue_data.get(week, {"total_revenue": 0,
                                           "cash_revenue": 0,
                                           "card_revenue": 0,
                                           "total_cost": 0,
                                           "total_profit": 0})}
                for week in full_weeks
            ]

        elif period == 'monthly':
            # Обчислюємо перший день місяця для from_date та to_date
            def first_day_of_month(date_obj):
                return date_obj.replace(day=1)

            start_month = first_day_of_month(filters.from_date.date())
            end_month = first_day_of_month(filters.to_date.date())
            full_months = []
            cur = start_month
            while cur <= end_month:
                full_months.append(cur)
                # Обчислюємо наступний місяць
                if cur.month == 12:
                    cur = cur.replace(year=cur.year + 1, month=1)
                else:
                    cur = cur.replace(month=cur.month + 1)
            revenue_data = {(row['date'].date() if isinstance(row['date'], datetime) else row['date']): {
                "total_revenue": row['total_revenue'],
                "cash_revenue": row['cash_revenue'],
                "card_revenue": row['card_revenue'],
                "total_cost": row['total_cost'],
                "total_profit": row['total_profit']
            } for row in result}
            return [
                {"date": month,
                 **revenue_data.get(month, {"total_revenue": 0,
                                            "cash_revenue": 0,
                                            "card_revenue": 0,
                                            "total_cost": 0,
                                            "total_profit": 0})}
                for month in full_months
            ]

        else:
            raise ValueError("Invalid period. Allowed values: daily, weekly, monthly.")