import json

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict

from app.schemas.websockets import SOrderBroadcast, SOrderItemBroadcast, STableBroadcast

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


async def broadcast_order_update(order_id: int, data):
    for connection in order_connections[order_id]:
        await connection.send_text(data)


async def broadcast_order(order):
    json_data = SOrderBroadcast.model_validate(order).model_dump_json()
    await broadcast_update("orders", json_data)

    if order.id in order_connections:
        await broadcast_order_update(order.id, json_data)


async def broadcast_order_item(order_item, deleted=False):
    if deleted:
        json_data = json.dumps({'id': order_item.id, 'deleted': True, 'broadcast_type': 'order_item'})
    else:
        json_data = SOrderItemBroadcast.model_validate(order_item).model_dump_json()
    if order_item.order.id in order_connections:
        await broadcast_order_update(order_item.order.id, json_data)


async def broadcast_table(table):
    await broadcast_update("tables", STableBroadcast.model_validate(table).model_dump_json())
