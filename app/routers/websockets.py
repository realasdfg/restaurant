from fastapi import APIRouter, WebSocket, Query, Depends, HTTPException

from starlette import status

from app.dependencies import users_service
from app.services.users import UsersService
from app.utils.users import get_current_user
from app.services.websockets import handle_websocket

router = APIRouter(prefix="/ws")


@router.websocket("/orders")
async def websocket_orders(websocket: WebSocket, token: str = Query(...),
                           user_service: UsersService = Depends(users_service)):
    try:
        await get_current_user(token, user_service)
        await handle_websocket(websocket, "orders")
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


@router.websocket("/orders/{order_id}")
async def websocket_order_detail(websocket: WebSocket, order_id: int, token: str = Query(...),
                                 user_service: UsersService = Depends(users_service)):
    try:
        await get_current_user(token, user_service)
        await handle_websocket(websocket, "orders", order_id=order_id)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


@router.websocket("/tables")
async def websocket_tables(websocket: WebSocket, token: str = Query(...),
                           user_service: UsersService = Depends(users_service)):
    try:
        await get_current_user(token, user_service)
        await handle_websocket(websocket, "tables")
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
