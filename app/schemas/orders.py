import enum
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderTypeEnum(enum.Enum):
    DINEIN = "dinein"
    TOGO = "togo"


class STableCreation(BaseModel):
    name: str = Field(..., max_length=20)


class STable(STableCreation):
    is_free: bool = True


class STableResponse(STable):
    id: int


class SOrderCreation(BaseModel):
    type: OrderTypeEnum
    table_id: int | None = None


class SOrder(SOrderCreation):
    created_by: int
    created_at: datetime
    paid: bool = False
    paid_at: datetime | None
    paid_by_card: Decimal = 0
    paid_by_cash: Decimal = 0
    paid_by: int | None


class SOrderEdit(SOrderCreation):
    type: OrderTypeEnum | None = None
    table_id: int | None = None
    paid: bool | None = None
    paid_by_card: Decimal | None = None
    paid_by_cash: Decimal | None = None


class SOrderResponse(SOrder):
    id: int


class SOrderItem(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int


class SMenuItemResponse(SOrderItem):
    id: int


class SOrderItem(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int


class SOrderItemResponse(SOrderItem):
    id: int
