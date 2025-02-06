from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.menu import MenuItem
from app.models.orders import Table, Order, OrderItem
from app.models.users import User
from app.schemas.orders import STableResponse, SOrderResponse, OrderTypeEnum, SOrderCreation, SOrderEdit, \
    SOrderItemResponse, STableCreation
from app.schemas.users import RoleEnum
from app.services.auth import get_current_user
from app.services.roles import role_required, has_access
from app.services.websockets import broadcast_order, broadcast_table

router = APIRouter(
    prefix='',
    tags=['Orders']
)


@router.post('/tables')
async def add_table(table: STableCreation,
                    session: AsyncSession = Depends(get_async_session),
                    current_user: User = Depends(role_required(RoleEnum.ADMIN))) -> STableResponse:
    new_table = Table(name=table.name)
    session.add(new_table)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Table with this name already exists")
    return STableResponse.model_validate(new_table, from_attributes=True)


@router.get('/tables')
async def get_tables(session: AsyncSession = Depends(get_async_session)) -> list[STableResponse]:
    result = await session.execute(select(Table))
    tables = result.scalars().all()
    return [STableResponse.model_validate(table, from_attributes=True) for table in tables]


@router.get('/tables/{table_id}')
async def get_table(table_id: int,
                    session: AsyncSession = Depends(get_async_session)) -> STableResponse:
    result = await session.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return STableResponse.model_validate(table, from_attributes=True)


@router.put('/tables/{table_id}')
async def update_table(table_id: int,
                       table_data: STableCreation,
                       session: AsyncSession = Depends(get_async_session),
                       current_user: User = Depends(role_required(RoleEnum.ADMIN))) -> STableResponse:
    result = await session.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    table.name = table_data.name
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Table with this name already exists")
    return STableResponse.model_validate(table, from_attributes=True)


@router.delete('/tables/{table_id}')
async def delete_table(table_id: int, session: AsyncSession = Depends(get_async_session),
                       current_user: User = Depends(role_required(RoleEnum.ADMIN))):
    result = await session.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    await session.delete(table)
    await session.commit()
    return {"status": 200, "message": "Table deleted"}


@router.post('/orders')
async def add_order(order: SOrderCreation,
                    session: AsyncSession = Depends(get_async_session),
                    current_user: User = Depends(role_required(RoleEnum.STAFF))) -> SOrderResponse:
    if order.type == OrderTypeEnum.DINEIN and order.table_id is None:
        raise HTTPException(status_code=400, detail="Order with 'dine in' type must have table_id.")
    new_order = Order(
        type=order.type,
        created_by=current_user.id,
    )
    if order.type == OrderTypeEnum.DINEIN:
        table_query = select(Table).where(Table.id == order.table_id)
        table_result = await session.execute(table_query)
        table = table_result.scalar_one_or_none()
        if table is None:
            raise HTTPException(status_code=404, detail="Table with this ID does not exist.")
        if not table.is_free:
            raise HTTPException(status_code=400, detail="Table is already occupied.")

        new_order.table_id = order.table_id
        table.is_free = False

    session.add(new_order)
    try:
        await session.commit()
        await session.refresh(new_order)
        await broadcast_order(new_order)
        if order.type == OrderTypeEnum.DINEIN:
            await broadcast_table(new_order.table)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Failed to create order due to a database error.")
    return SOrderResponse.model_validate(new_order, from_attributes=True)


@router.get('/orders')
async def get_orders(current_only: bool, session: AsyncSession = Depends(get_async_session),
                     current_user: User = Depends(get_current_user)) -> list[SOrderResponse]:
    if not current_only:
        if not await has_access(current_user.role, RoleEnum.ADMIN):
            raise HTTPException(status_code=403, detail=f"Access denied")
        query = select(Order)
    else:
        query = select(Order).where(Order.paid == False)
    result = await session.execute(query.order_by(Order.created_at.desc()))
    orders = result.scalars().all()
    return [SOrderResponse.model_validate(order, from_attributes=True) for order in orders]


@router.get('/orders/{order_id}')
async def get_order(order_id: int, session: AsyncSession = Depends(get_async_session),
                    current_user: User = Depends(get_current_user)) -> SOrderResponse:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.paid and not await has_access(current_user.role, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail=f"Access denied")
    return SOrderResponse.model_validate(order, from_attributes=True)


@router.patch('/orders/{order_id}')
async def update_order(order_id: int,
                       order_data: SOrderEdit,
                       session: AsyncSession = Depends(get_async_session),
                       current_user: User = Depends(role_required(RoleEnum.STAFF))) -> SOrderResponse:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.paid:
        raise HTTPException(status_code=403, detail="Order cannot be changed after payment")

    old_table = order.table

    if order_data.paid:
        if order_data.type or order_data.table_id:
            raise HTTPException(status_code=400,
                                detail="Can't close order and change its type or table at the same time")
        if not order_data.paid_by_card and not order_data.paid_by_cash:
            raise HTTPException(status_code=400, detail="Must be provided some sums for payment")
        order.paid = True
        order.paid_at = datetime.now()
        order.paid_by_cash = order_data.paid_by_cash
        order.paid_by_card = order_data.paid_by_card
        if order.table:
            order.table.is_free = True
    else:
        if order_data.paid_by_card or order_data.paid_by_cash:
            raise HTTPException(status_code=400, detail="Can change payment sum during order closing only")

        if order_data.type:
            order.type = order_data.type
        if order.type == OrderTypeEnum.TOGO:
            order.table.is_free = True
            order.table_id = None
        elif order.type == OrderTypeEnum.DINEIN:
            if order_data.table_id is None:
                raise HTTPException(status_code=400, detail="Order with 'dine in' type must have table_id.")
            table_result = await session.execute(select(Table).where(Table.id == order_data.table_id))
            table = table_result.scalar_one_or_none()
            if table is None:
                raise HTTPException(status_code=404, detail="Table with this ID does not exist.")
            if not table.is_free:
                raise HTTPException(status_code=400, detail="Table is already occupied.")
            if order.table:
                order.table.is_free = True
            order.table = table
            order.table.is_free = False

    await session.commit()
    await broadcast_order(order)
    await broadcast_table(order.table)
    if old_table:
        await broadcast_table(old_table)
    return SOrderResponse.model_validate(order, from_attributes=True)

@router.patch('/orders/{order_id}/menu-items/{item_id}')
async def add_or_update_order_item(order_id: int, item_id: int,
                                   quantity: int | None = None,
                                   session: AsyncSession = Depends(get_async_session),
                                   current_user: User = Depends(role_required(RoleEnum.STAFF))) -> SOrderItemResponse:
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
            quantity=quantity
        )
        session.add(order_item)
    try:
        await session.commit()
        await session.refresh(order_item)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Failed to add item to the order due to a database error.")
    return SOrderItemResponse.model_validate(order_item, from_attributes=True)


@router.get('/orders/{order_id}/menu-items')
async def get_order_items(order_id: int,
                          session: AsyncSession = Depends(get_async_session)) -> list[SOrderItemResponse]:
    result = await session.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    order_items = result.scalars().all()
    return [SOrderItemResponse.model_validate(order_item, from_attributes=True) for order_item in order_items]


@router.get('/orders/{order_id}/menu-items/{item_id}')
async def get_order_item(order_id: int, item_id: int,
                         session: AsyncSession = Depends(get_async_session)) -> SOrderItemResponse:
    order_item_result = await session.execute(select(OrderItem)
                                              .where(OrderItem.order_id == order_id)
                                              .where(OrderItem.menu_item_id == item_id))
    order_item = order_item_result.scalar_one_or_none()
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order, menu item or item in order does not exist.")
    return SOrderItemResponse.model_validate(order_item, from_attributes=True)


@router.delete('/orders/{order_id}/menu-items/{item_id}')
async def delete_order_item(order_id: int, item_id: int,
                            session: AsyncSession = Depends(get_async_session),
                            current_user: User = Depends(role_required(RoleEnum.STAFF))):
    order_item_result = await session.execute(select(OrderItem)
                                              .where(OrderItem.order_id == order_id)
                                              .where(OrderItem.menu_item_id == item_id))
    order_item = order_item_result.scalar_one_or_none()
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order, menu item or item in order does not exist.")
    await session.delete(order_item)
    await session.commit()
    return {"status": 200, "message": "Order item deleted"}
