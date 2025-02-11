import json

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict

from app.schemas.orders import SOrder, STable, SOrderItemResponse

active_connections: Dict[str, List[WebSocket]] = {
    "orders": [],
    "tables": [],
}

order_connections: Dict[int, List[WebSocket]] = {}


async def handle_websocket(websocket: WebSocket, connection_type: str, order_id: int = None):
    await websocket.accept()

    if order_id is not None:
        if order_id not in order_connections:
            order_connections[order_id] = []
        order_connections[order_id].append(websocket)
    else:
        active_connections[connection_type].append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if order_id is not None:
            order_connections[order_id].remove(websocket)
            if not order_connections[order_id]:
                del order_connections[order_id]
        else:
            active_connections[connection_type].remove(websocket)


async def broadcast_update(connection_type: str, data):
    for connection in active_connections[connection_type]:
        await connection.send_text(data)


async def broadcast_order(order=None, order_item=None, deleted=False):
    if order:
        json_data = SOrder.model_validate(order, from_attributes=True).model_dump_json()
        await broadcast_update("orders", json_data)

        if order.id in order_connections:
            for connection in order_connections[order.id]:
                await connection.send_text(json_data)

    if order_item:
        if deleted:
            json_data = json.dumps({'id': order_item.id, 'deleted': True})
        else:
            json_data = SOrderItemResponse.model_validate(order_item, from_attributes=True).model_dump_json()
        if order_item.order.id in order_connections:
            for connection in order_connections[order_item.order.id]:
                await connection.send_text(json_data)


async def broadcast_table(table):
    await broadcast_update("tables", STable.model_validate(table, from_attributes=True).model_dump_json())
