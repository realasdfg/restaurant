from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError

from app.dependencies import tables_service, orders_service
from app.models.users import User
from app.schemas.orders import SOrderPublicResponse
from app.schemas.tables import STableAdd, STable, STableOrdersFilter
from app.models.enums import RoleEnum
from app.services.orders import OrdersService
from app.services.tables import TablesService
from app.utils.roles import has_access
from app.utils.users import get_current_user_if_role, get_current_user_if_role_or_none

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
async def get_tables(table_service: TablesService = Depends(tables_service), include_deleted: bool = False,
                     current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))) -> list[STable]:
    if include_deleted and not has_access(current_user.role, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail="Forbidden")
    tables = await table_service.get_tables(include_deleted)
    return [STable.model_validate(table) for table in tables]


@router.get('/{table_id}')
async def get_table(table_id: int, include_deleted: bool = False,
                    table_service: TablesService = Depends(tables_service),
                    current_user: User = Depends(get_current_user_if_role_or_none(RoleEnum.ADMIN))) -> STable:
    if include_deleted and current_user is None:
        raise HTTPException(status_code=403, detail="Forbidden")
    table = await table_service.get_table_by_id(table_id, include_deleted)
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
    return {"status": 200, "detail": f"Table with id {table_id} deleted"}


@router.get('/{table_id}/orders')
async def get_table_orders(table_id: int, filters: STableOrdersFilter = Depends(),
                           order_service: OrdersService = Depends(orders_service)) -> list[SOrderPublicResponse]:
    if not filters.current_only:
        raise HTTPException(status_code=403, detail="Forbidden. Try to use current_only=true parameter")
    orders = await order_service.get_all({'table_id': table_id, 'paid': False})
    return [SOrderPublicResponse.model_validate(order) for order in orders]
