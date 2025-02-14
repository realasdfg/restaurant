from app.schemas.orders import SOrder, SOrderItemPublicResponse
from app.schemas.tables import STable


class SOrderBroadcast(SOrder):
    broadcast_type: str = 'order'


class SOrderItemBroadcast(SOrderItemPublicResponse):
    broadcast_type: str = 'order_item'


class STableBroadcast(STable):
    broadcast_type: str = 'table'
