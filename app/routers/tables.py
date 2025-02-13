from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError

from app.dependencies import tables_service
from app.models.users import User
from app.schemas.tables import STableAdd, STable
from app.schemas.users import RoleEnum
from app.services.tables import TablesService
from app.utils.users import get_current_user_if_role

router = APIRouter(
    prefix='/tables',
    tags=['Tables']
)


@router.post('')
async def add_table(table_data: STableAdd, table_service: TablesService = Depends(tables_service),
                    current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> STable:
    try:
        table = await table_service.add_table(table_data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Table with this name already exists")
    return STable.model_validate(table)


@router.get('')
async def get_tables(table_service: TablesService = Depends(tables_service),
                     current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))) -> list[STable]:
    tables = await table_service.get_tables()
    return [STable.model_validate(table) for table in tables]


@router.get('/{table_id}')
async def get_table(table_id: int, table_service: TablesService = Depends(tables_service)) -> STable:
    table = await table_service.get_table_by_id(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return STable.model_validate(table)


@router.put('/{table_id}')
async def update_table(table_id: int, table_data: STableAdd, table_service: TablesService = Depends(tables_service),
                       current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> STable:
    try:
        table = await table_service.update_table_by_id(table_id, table_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Table with this name already exists")
    return STable.model_validate(table)


@router.delete('/{table_id}')
async def delete_table(table_id: int, table_service: TablesService = Depends(tables_service),
                       current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
    try:
        await table_service.delete_table_by_id(table_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": 200, "message": f"Table with id {table_id} deleted"}
