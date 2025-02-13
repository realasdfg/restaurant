from datetime import datetime

from fastapi import HTTPException

from app.models.orders import Order
from app.models.users import User
from app.schemas.orders import SOrderAdd, SOrderFilter, SOrderEdit
from app.models.enums import OrderTypeEnum
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
        order_data_dict = order_data.model_dump(exclude_unset=True)
        if order.paid_online:
            if order_data.paid_by_cash is not None or order_data.paid_by_card is not None:
                raise HTTPException(status_code=422, detail="Order is already paid online. Can't provide sums to it.")
        else:
            if order_data.paid_by_cash is None or order_data.paid_by_card is None:
                raise HTTPException(status_code=422,
                                    detail="Must be provided some sums (paid_by_card or/and paid_by_cash) for payment")
            order_data_dict['paid_at'] = datetime.now()
        order_data_dict['paid_by'] = current_user.id
        updated_order = await self._update(order.id, order_data_dict)
        if order.table:
            await table_service.set_is_free(updated_order.table_id, False)
        return updated_order

    async def provide_order_payment_online(self, order: Order, order_data: SOrderEdit):
        order_data_dict = order_data.model_dump(exclude_unset=True)
        order_data_dict['paid_at'] = datetime.now()
        order_data_dict['paid_by_card'] = 9999
        updated_order = await self._update(order.id, order_data_dict)
        return updated_order
