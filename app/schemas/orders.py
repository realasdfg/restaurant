import enum
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderTypeEnum(enum.Enum):
    DINEIN = "dinein"
    TOGO = "togo"


class STable(BaseModel):
    name: str = Field(..., max_length=20)


class STableResponse(STable):
    id: int


class SOrder(BaseModel):
    type: OrderTypeEnum
    created_by: int
    created_at: datetime
    paid: bool = False
    paid_at: datetime | None
    paid_by_card: Decimal = 0
    paid_by_cash: Decimal = 0
    table_id: int | None


class SOrderResponse(SOrder):
    id: int


class SOrderItem(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int


class SMenuItemResponse(SOrderItem):
    id: int
