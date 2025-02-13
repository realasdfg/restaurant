from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import orders_service, tables_service
from app.models.menu import MenuItem
from app.models.orders import Order, OrderItem
from app.models.users import User
from app.schemas.orders import SOrder, SOrderAdd, SOrderEdit, SOrderItem, SOrderFilter
from app.models.enums import OrderTypeEnum, RoleEnum
from app.services.orders import OrdersService
from app.services.tables import TablesService
from app.utils.users import get_current_user_if_role, has_access, get_current_user
from app.services.websockets import broadcast_order, broadcast_table

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
        if order_data.type == OrderTypeEnum.DINEIN:
            await broadcast_table(order.table)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError as e:
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
    old_table = order.table

    updated_order = None
    if order_data.paid is not None:
        updated_order = await order_service.provide_order_payment(order, order_data, table_service, current_user)
    elif order_data.type is not None or order_data.table_id is not None:
        updated_order = await order_service.update_order_info(order, order_data, table_service)
    elif order_data.paid_online is not None:
        updated_order = await order_service.provide_order_payment_online(order, order_data)

    await broadcast_order(updated_order)
    if order.table:
        await broadcast_table(order.table)
    if old_table:
        await broadcast_table(old_table)
    return SOrder.model_validate(updated_order)


@router.patch('/{order_id}/menu-items/{item_id}')
async def add_or_update_order_item(order_id: int, item_id: int,
                                   quantity: int | None = None,
                                   session: AsyncSession = Depends(get_async_session),
                                   current_user: User = Depends(
                                       get_current_user_if_role(RoleEnum.STAFF))) -> SOrderItem:
    order_item_result = await session.execute(select(OrderItem)
                                              .where(OrderItem.order_id == order_id)
                                              .where(OrderItem.menu_item_id == item_id))
    order_item = order_item_result.scalar_one_or_none()

    if order_item:
        if quantity:
            order_item.quantity = quantity
        else:
            order_item.quantity += 1
    else:
        order_result = await session.execute(select(Order).where(Order.id == order_id))
        order = order_result.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order with this ID does not exist.")
        menu_item_result = await session.execute(select(MenuItem).where(MenuItem.id == item_id))
        menu_item = menu_item_result.scalar_one_or_none()
        if menu_item is None:
            raise HTTPException(status_code=404, detail="Menu item with this ID does not exist.")

        order_item = OrderItem(
            order_id=order_id,
            menu_item_id=item_id,
            quantity=quantity,
            cost=menu_item.cost,
            price=menu_item.price,
            type=menu_item.type,
            weight=menu_item.weight,
        )
        session.add(order_item)
    try:
        await session.commit()
        await session.refresh(order_item)
        await broadcast_order(order_item=order_item)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Failed to add item to the order due to a database error.")
    return SOrderItem.model_validate(order_item, from_attributes=True)


@router.get('/{order_id}/menu-items')
async def get_order_items(order_id: int,
                          session: AsyncSession = Depends(get_async_session)) -> list[SOrderItem]:
    result = await session.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    order_items = result.scalars().all()
    return [SOrderItem.model_validate(order_item, from_attributes=True) for order_item in order_items]


@router.get('/{order_id}/menu-items/{item_id}')
async def get_order_item(order_id: int, item_id: int,
                         session: AsyncSession = Depends(get_async_session)) -> SOrderItem:
    order_item_result = await session.execute(select(OrderItem)
                                              .where(OrderItem.order_id == order_id)
                                              .where(OrderItem.menu_item_id == item_id))
    order_item = order_item_result.scalar_one_or_none()
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order, menu item or item in order does not exist.")
    return SOrderItem.model_validate(order_item, from_attributes=True)


@router.delete('/{order_id}/menu-items/{item_id}')
async def delete_order_item(order_id: int, item_id: int,
                            session: AsyncSession = Depends(get_async_session),
                            current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))):
    order_item_result = await session.execute(select(OrderItem)
                                              .where(OrderItem.order_id == order_id)
                                              .where(OrderItem.menu_item_id == item_id))
    order_item = order_item_result.scalar_one_or_none()
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order, menu item or item in order does not exist.")
    await session.delete(order_item)
    await session.commit()
    await broadcast_order(order_item=order_item, deleted=True)
    return {"status": 200, "message": "Order item deleted"}
