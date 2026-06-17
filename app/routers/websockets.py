from fastapi import APIRouter, WebSocket, Query, Depends, HTTPException

from starlette import status

from app.dependencies import users_service
from app.services.users import UsersService
from app.utils.users import get_current_user
from app.services.websockets import handle_websocket


class WebsocketRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/ws")
        self.router.add_api_websocket_route("/orders", self.websocket_orders, name="orders")
        self.router.add_api_websocket_route("/orders/{order_id}", self.websocket_order_detail, name="order_detail")
        self.router.add_api_websocket_route("/tables", self.websocket_tables, name="tables")

    async def websocket_orders(self, websocket: WebSocket, token: str = Query(...),
                               user_service: UsersService = Depends(users_service)):
        try:
            await get_current_user(token, user_service)
            await handle_websocket(websocket, "orders")
        except HTTPException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    async def websocket_order_detail(self, websocket: WebSocket, order_id: int, token: str = Query(...),
                                     user_service: UsersService = Depends(users_service)):
        try:
            await get_current_user(token, user_service)
            await handle_websocket(websocket, "orders", order_id=order_id)
        except HTTPException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    async def websocket_tables(self, websocket: WebSocket, token: str = Query(...),
                               user_service: UsersService = Depends(users_service)):
        try:
            await get_current_user(token, user_service)
            await handle_websocket(websocket, "tables")
        except HTTPException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
