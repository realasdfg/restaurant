import enum
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator

from app.schemas.menu import MenuItemTypeEnum


class OrderTypeEnum(enum.Enum):
    DINEIN = "dinein"
    TOGO = "togo"


class STableAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)


class STable(STableAdd):
    id: int
    is_free: bool = True
    is_deleted: bool = False


class SOrderAdd(BaseModel):
    type: OrderTypeEnum
    table_id: int | None = None


class SOrderEdit(SOrderAdd):
    type: OrderTypeEnum | None = None
    table_id: int | None = None
    paid: bool | None = None
    paid_by_card: Decimal | None = None
    paid_by_cash: Decimal | None = None
    paid_online: bool | None = None


class SOrder(SOrderAdd):
    id: int
    created_by: int
    created_at: datetime
    paid: bool = False
    paid_at: datetime | None
    paid_by_card: Decimal = 0
    paid_by_cash: Decimal = 0
    paid_online: bool = False
    paid_by: int | None


class SOrderFilter(BaseModel):
    current_only: bool | None = None
    paid_only: bool | None = None
    from_created_date: datetime | None = None
    to_created_date: datetime | None = None
    type: OrderTypeEnum | None = None
    created_by: int | None = None
    paid_by: int | None = None

    @model_validator(mode='after')
    def validate_model(self):
        if self.current_only and self.paid_only:
            raise HTTPException(status_code=400, detail="current_only and paid_only cannot both be True.")
        return self


class SOrderItem(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    cost: Decimal
    price: Decimal
    type: MenuItemTypeEnum
    weight: int
