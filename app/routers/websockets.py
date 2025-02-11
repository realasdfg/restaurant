from fastapi import APIRouter, WebSocket, Query, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database import get_async_session
from app.services.auth import get_current_user
from app.services.websockets import handle_websocket

router = APIRouter()

@router.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket, token: str = Query(...),
                           session: AsyncSession = Depends(get_async_session)):
    try:
        await get_current_user(session, token)
        await handle_websocket(websocket, "orders")
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


@router.websocket("/ws/orders/{order_id}")
async def websocket_order_detail(websocket: WebSocket, order_id: int, token: str = Query(...),
                                 session: AsyncSession = Depends(get_async_session)):
    try:
        await get_current_user(session, token)
        await handle_websocket(websocket, "orders", order_id=order_id)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


@router.websocket("/ws/tables")
async def websocket_tables(websocket: WebSocket, token: str = Query(...),
                           session: AsyncSession = Depends(get_async_session)):
    try:
        await get_current_user(session, token)
        await handle_websocket(websocket, "tables")
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)