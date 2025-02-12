from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.tables import Table
from app.models.users import User
from app.routers.orders import router
from app.schemas.tables import STableAdd, STable
from app.schemas.users import RoleEnum
from app.utils.users import get_current_user_if_role


@router.post('/tables')
async def add_table(table: STableAdd,
                    session: AsyncSession = Depends(get_async_session),
                    current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> STable:
    new_table = Table(name=table.name)
    session.add(new_table)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Table with this name already exists")
    return STable.model_validate(new_table, from_attributes=True)


@router.get('/tables')
async def get_tables(session: AsyncSession = Depends(get_async_session)) -> list[STable]:
    result = await session.execute(select(Table))
    tables = result.scalars().all()
    return [STable.model_validate(table, from_attributes=True) for table in tables]


@router.get('/tables/{table_id}')
async def get_table(table_id: int,
                    session: AsyncSession = Depends(get_async_session)) -> STable:
    result = await session.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return STable.model_validate(table, from_attributes=True)


@router.put('/tables/{table_id}')
async def update_table(table_id: int,
                       table_data: STableAdd,
                       session: AsyncSession = Depends(get_async_session),
                       current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> STable:
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
    return STable.model_validate(table, from_attributes=True)


@router.delete('/tables/{table_id}')
async def delete_table(table_id: int, session: AsyncSession = Depends(get_async_session),
                       current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
    result = await session.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    await session.delete(table)
    await session.commit()
    return {"status": 200, "message": "Table deleted"}
