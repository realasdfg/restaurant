from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.orders import Table, Order
from app.models.users import User
from app.schemas.orders import STable, STableResponse, SOrderResponse, OrderTypeEnum, SOrderCreation, SOrderEdit
from app.schemas.users import RoleEnum
from app.services.auth import get_current_user
from app.services.roles import role_required

router = APIRouter(
    prefix='',
    tags=['Orders']
)


@router.post('/tables')
async def add_table(table: STable,
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
async def update_menu_category(table_id: int,
                               table_data: STable,
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
async def delete_menu_category(table_id: int, session: AsyncSession = Depends(get_async_session),
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

        new_order.table_id = order.table_id

    session.add(new_order)
    try:
        await session.commit()
        await session.refresh(new_order)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Failed to create order due to a database error.")
    return SOrderResponse.model_validate(new_order, from_attributes=True)


@router.get('/orders')
async def get_orders(session: AsyncSession = Depends(get_async_session),
                     current_user: User = Depends(get_current_user)) -> list[SOrderResponse]:
    result = await session.execute(select(Order))
    orders = result.scalars().all()
    return [SOrderResponse.model_validate(order, from_attributes=True) for order in orders]


@router.get('/orders/{order_id}')
async def get_menu_item(order_id: int, session: AsyncSession = Depends(get_async_session),
                        current_user: User = Depends(get_current_user)) -> SOrderResponse:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return SOrderResponse.model_validate(order, from_attributes=True)


@router.put('/orders/{order_id}')
async def update_menu_item(order_id: int,
                           order_data: SOrderEdit,
                           session: AsyncSession = Depends(get_async_session),
                           current_user: User = Depends(role_required(RoleEnum.STAFF))) -> SOrderResponse:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.paid:
        raise HTTPException(status_code=403, detail="Order cannot be changed after payment")

    if order_data.paid:
        if order_data.type or order_data.table_id:
            raise HTTPException(status_code=400,
                                detail="Can't close order and change its type or table at the same time")
        if not order_data.paid_by_card or not order_data.paid_by_cash:
            raise HTTPException(status_code=400, detail="Must be provided some sums for payment")
        order.paid = True
        order.paid_at = datetime.now()
        order.paid_by_cash = order_data.paid_by_cash
        order.paid_by_card = order_data.paid_by_card
    else:
        if order_data.paid_by_card or order_data.paid_by_cash:
            raise HTTPException(status_code=400, detail="Can change payment sum during order closing only")

        if order_data.type:
            order.type = order_data.type
        if order.type == OrderTypeEnum.TOGO:
            order.table_id = None
        else:
            if order_data.table_id:
                table_result = await session.execute(select(Table).where(Table.id == order_data.table_id))
                table = table_result.scalar_one_or_none()
                if table is None:
                    raise HTTPException(status_code=404, detail="Table with this ID does not exist.")
                order.table_id = order_data.table_id

            if order.table_id is None:
                raise HTTPException(status_code=400, detail="Order with 'dine in' type must have table_id.")

    await session.commit()
    return SOrderResponse.model_validate(order, from_attributes=True)


@router.delete('/orders/{order_id}')
async def delete_menu_item(order_id: int, session: AsyncSession = Depends(get_async_session),
                           current_user: User = Depends(role_required(RoleEnum.ADMIN))):
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await session.delete(order)
    await session.commit()
    return {"status": 200, "message": "Order deleted"}
