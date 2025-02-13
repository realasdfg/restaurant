from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException

from app.models.orders import Order
from app.models.users import User
from app.schemas.orders import SOrderAdd, SOrderFilter, SOrderEdit
from app.models.enums import OrderTypeEnum, MenuItemTypeEnum
from app.services.crud_base import BaseCRUDService
from app.services.tables import TablesService


class OrdersService(BaseCRUDService):

    async def add_order(self, order_data: SOrderAdd, table_service: TablesService, current_user: User):
        if order_data.type == OrderTypeEnum.DINEIN:
            table = await table_service.get_table_by_id(order_data.table_id)
            if table is None:
                raise ValueError("Table not found")
            if not table.is_free:
                raise HTTPException(status_code=400, detail="Table is already occupied")
        order_dict = order_data.model_dump()
        order_dict["created_by"] = current_user.id
        order = await self._create(order_dict)
        if order_data.type == OrderTypeEnum.DINEIN:
            await table_service.set_is_free(order_data.table_id, False)
        return order

    async def get_orders(self, filters: SOrderFilter):
        filters_dict = filters.to_query_filters()
        return await self._get_all(filters_dict)

    async def get_order_by_id(self, order_id):
        return await self._get_one({'id': order_id})

    async def update_order_info(self, order: Order, order_data: SOrderEdit, table_service: TablesService):
        order_data_dict = order_data.model_dump(exclude_unset=True)
        if order_data_dict.get('type') == OrderTypeEnum.TOGO:
            order_data_dict['table_id'] = None
        elif order_data_dict.get('type') == OrderTypeEnum.DINEIN or order_data_dict.get('table_id'):
            new_table = await table_service.get_table_by_id(order_data.table_id)
            if new_table is None:
                raise ValueError("Table not found")
            if not new_table.is_free:
                raise HTTPException(status_code=400, detail="Table is already occupied.")

        updated_order = await self._update(order.id, order_data_dict)
        if order.table_id is not None:
            await table_service.set_is_free(order.table_id, True)
        if updated_order.table_id is not None:
            await table_service.set_is_free(updated_order.table_id, False)
        return updated_order

    async def provide_order_payment(self, order: Order, order_data: SOrderEdit, table_service: TablesService,
                                    current_user: User):
        if not order.order_items:
            raise HTTPException(status_code=400, detail="Can't provide order payment with 0 total sum order")
        order_data_dict = order_data.model_dump(exclude_unset=True)
        if order.paid_online:
            if order_data.paid_by_cash is not None or order_data.paid_by_card is not None:
                raise HTTPException(status_code=422, detail="Order is already paid online. Can't provide sums to it.")
        else:
            if order_data.paid_by_cash is None and order_data.paid_by_card is None:
                raise HTTPException(status_code=422,
                                    detail="Must be provided some sums (paid_by_card or/and paid_by_cash) for payment")

            provided_sum = order_data_dict.get('paid_by_card') if order_data_dict.get('paid_by_card') else Decimal(0)
            provided_sum += order_data_dict.get('paid_by_cash') if order_data_dict.get('paid_by_cash') else Decimal(0)
            total_sum = ((await self.calculate_order_total_sum(order=order))
                         .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            if provided_sum != total_sum:
                raise HTTPException(status_code=400,
                                    detail=f"Total order items sum ({total_sum}) must be equal to provided sum ({provided_sum})")
            order_data_dict['paid_at'] = datetime.now()
        order_data_dict['paid_by'] = current_user.id
        updated_order = await self._update(order.id, order_data_dict)
        if order.table:
            await table_service.set_is_free(updated_order.table_id, True)
        return updated_order

    async def provide_order_payment_online(self, order: Order, order_data: SOrderEdit):
        if not order.order_items:
            raise HTTPException(status_code=400, detail="Can't provide order payment with 0 total sum order")
        order_data_dict = order_data.model_dump(exclude_unset=True)
        order_data_dict['paid_at'] = datetime.now()
        order_data_dict['paid_by_card'] = ((await self.calculate_order_total_sum(order=order))
                                           .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        updated_order = await self._update(order.id, order_data_dict)
        return updated_order

    async def calculate_order_total_sum(self, order_id: int = None, order: Order = None) -> Decimal:
        if order is None:
            order = await self.get_order_by_id(order_id)
            if order is None:
                raise ValueError("Order not found")
        return Decimal(sum(item.price * item.quantity if item.type == MenuItemTypeEnum.BY_QUANTITY
                   else (item.quantity / Decimal(item.weight)) * item.price for item in order.order_items))
