from app.repositories.orders import OrdersRepository
from app.schemas.statistics import SOrdersRevenue


class StatisticsService:
    def __init__(self, order_repository: OrdersRepository):
        self._order_repo = order_repository

    async def get_total_profit(self, filters: SOrdersRevenue):
        return await self._order_repo.get_total_profit(filters.from_date, filters.to_date)

    async def get_daily_profit(self, filters: SOrdersRevenue):
        return await self._order_repo.get_daily_profit(filters.from_date, filters.to_date)
