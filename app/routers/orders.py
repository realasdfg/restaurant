from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.dependencies import orders_service, tables_service, menu_items_service, order_items_service
from app.models.users import User
from app.schemas.orders import SOrder, SOrderAdd, SOrderEdit, SOrderItem, SOrderFilter, SOrderItemAddOrEdit, \
    SOrderItemPublicResponse
from app.models.enums import RoleEnum
from app.services.menu import MenuItemsService
from app.services.orders import OrdersService, OrderItemsService
from app.services.tables import TablesService
from app.utils.users import get_current_user_if_role, has_access, get_current_user, get_current_user_if_role_or_none
from app.services.websockets import broadcast_order, broadcast_table, broadcast_order_item

router = APIRouter(
    prefix='/orders',
    tags=['Orders']
)


@router.post('')
async def add_order(order_data: SOrderAdd,
                    order_service: OrdersService = Depends(orders_service),
                    table_service: TablesService = Depends(tables_service),
                    current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))) -> SOrder:
    try:
        order = await order_service.add_order(order_data, table_service, current_user)
        await broadcast_order(order)
        if order.table_id:
            table = await table_service.get_table_by_id(order.table_id)
            await broadcast_table(table)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Failed to create order due to a database error.")
    return SOrder.model_validate(order)


@router.get('')
async def get_orders(filters: SOrderFilter = Depends(), order_service: OrdersService = Depends(orders_service),
                     current_user: User = Depends(get_current_user)) -> list[SOrder]:
    if filters.paid is not False and not await has_access(current_user.role, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail=f"Access denied. Try to use paid=false parameter")
    orders = await order_service.get_orders(filters)
    return [SOrder.model_validate(order) for order in orders]


@router.get('/{order_id}')
async def get_order(order_id: int, order_service: OrdersService = Depends(orders_service),
                    current_user: User = Depends(get_current_user)) -> SOrder:
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.paid and not await has_access(current_user.role, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail=f"Access denied")
    return SOrder.model_validate(order)


@router.patch('/{order_id}')
async def update_order(order_id: int, order_data: SOrderEdit,
                       order_service: OrdersService = Depends(orders_service),
                       table_service: TablesService = Depends(tables_service),
                       current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))) -> SOrder:
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.paid:
        raise HTTPException(status_code=403, detail="Order cannot be changed after payment")

    updated_order = None
    try:
        if order_data.paid is not None:
            updated_order = await order_service.provide_order_payment(order, order_data, table_service, current_user)
        elif order_data.type is not None or order_data.table_id is not None:
            updated_order = await order_service.update_order_info(order, order_data, table_service)
        elif order_data.paid_online is not None:
            updated_order = await order_service.provide_order_payment_online(order, order_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Failed to update order due to a database error.")
    await broadcast_order(updated_order)
    if updated_order.table_id:
        table = await table_service.get_table_by_id(updated_order.table_id)
        await broadcast_table(table)
    if order.table_id:
        old_table = await table_service.get_table_by_id(order.table_id)
        await broadcast_table(old_table)
    return SOrder.model_validate(updated_order)


@router.patch('/{order_id}/menu-items/{menu_item_id}')
async def add_or_update_order_item(order_id: int, menu_item_id: int, order_item_data: SOrderItemAddOrEdit,
                                   order_item_service: OrderItemsService = Depends(order_items_service),
                                   order_service: OrdersService = Depends(orders_service),
                                   menu_item_service: MenuItemsService = Depends(menu_items_service),
                                   current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))
                                   ) -> SOrderItem:
    try:
        order_item = await order_item_service.get_order_item(order_id, menu_item_id, order_service, menu_item_service)
        if order_item:
            order_item = await order_item_service.update_order_item_quantity(order_id, menu_item_id, order_item_data,
                                                                             order_service, menu_item_service)
        else:
            order_item = await order_item_service.add_order_item(order_id, menu_item_id, order_item_data, order_service,
                                                                 menu_item_service)
        await broadcast_order_item(order_item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Failed to add item to the order due to a database error.")
    return SOrderItem.model_validate(order_item)


@router.get('/{order_id}/menu-items')
async def get_order_items(order_id: int, order_item_service: OrderItemsService = Depends(order_items_service),
                          order_service: OrdersService = Depends(orders_service),
                          current_user: User | None = Depends(get_current_user_if_role_or_none(RoleEnum.STAFF))
                          ) -> list[SOrderItemPublicResponse] | list[SOrderItem]:
    try:
        order_items = await order_item_service.get_order_items(order_id, order_service)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if current_user is None:
        return [SOrderItemPublicResponse.model_validate(order_item) for order_item in order_items]
    else:
        return [SOrderItem.model_validate(order_item) for order_item in order_items]


@router.get('/{order_id}/menu-items/{menu_item_id}')
async def get_order_item(order_id: int, menu_item_id: int,
                         order_item_service: OrderItemsService = Depends(order_items_service),
                         order_service: OrdersService = Depends(orders_service),
                         menu_item_service: MenuItemsService = Depends(menu_items_service),
                         current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))) -> SOrderItem:
    try:
        order_item = await order_item_service.get_order_item(order_id, menu_item_id, order_service, menu_item_service)
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order item not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return SOrderItem.model_validate(order_item)


@router.delete('/{order_id}/menu-items/{menu_item_id}')
async def delete_order_item(order_id: int, menu_item_id: int,
                            order_item_service: OrderItemsService = Depends(order_items_service),
                            order_service: OrdersService = Depends(orders_service),
                            menu_item_service: MenuItemsService = Depends(menu_items_service),
                            current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))):
    try:
        order_item = await order_item_service.delete_order_item(order_id, menu_item_id, order_service,
                                                                menu_item_service)
        await broadcast_order_item(order_item, deleted=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": 200, "detail": f"Order item with id {order_item.id} deleted"}
