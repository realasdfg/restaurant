from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict

router = APIRouter()

active_connections: Dict[str, List[WebSocket]] = {
    "orders": [],
    "tables": []
}


async def handle_websocket(websocket: WebSocket, connection_type: str):
    await websocket.accept()
    active_connections[connection_type].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[connection_type].remove(websocket)


@router.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    await handle_websocket(websocket, "orders")


@router.websocket("/ws/tables")
async def websocket_tables(websocket: WebSocket):
    await handle_websocket(websocket, "tables")


async def broadcast_update(connection_type: str, data):
    for connection in active_connections[connection_type]:
        await connection.send_json(data)


async def broadcast_order(order):
    await broadcast_update("orders", order)


async def broadcast_table(table):
    await broadcast_update("tables", table)
