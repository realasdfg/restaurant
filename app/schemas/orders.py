from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator, Field

from app.models.enums import OrderTypeEnum, MenuItemTypeEnum
from app.models.orders import Order


class SOrderAdd(BaseModel):
    type: OrderTypeEnum
    table_id: int | None = None

    class Config:
        extra = 'forbid'

    @model_validator(mode='after')
    def check_table_id(self):
        if self.type == OrderTypeEnum.DINEIN and self.table_id is None:
            raise ValueError("Order with 'dine in' type must have table_id.")
        elif self.type == OrderTypeEnum.TOGO and self.table_id is not None:
            raise ValueError("Order with 'to go' type must not have table_id.")
        return self


class SOrderEdit(SOrderAdd):
    type: OrderTypeEnum = None
    table_id: int | None = None
    paid: bool = None
    paid_by_card: Decimal = None
    paid_by_cash: Decimal = None
    paid_online: bool = None

    @model_validator(mode='after')
    def validate_model(self):
        group1 = {self.type, self.table_id} - {None}
        group2 = {self.paid, self.paid_by_card, self.paid_by_cash} - {None}
        group3 = {self.paid_online} - {None}
        filled_groups = sum(bool(group) for group in [group1, group2, group3])
        if filled_groups != 1:
            raise ValueError("Only one of the following groups should be provided: "
                             "(type, table_id), (paid, paid_by_card, paid_by_cash), or (paid_online)")
        if group2:
            if self.paid is None or self.paid is False:
                raise ValueError("Can change paid value only to true")
        if self.paid_online is False:
            raise ValueError("Can change paid_online value only to true")
        return self


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

    class Config:
        from_attributes = True


class SOrderPublicResponse(BaseModel):
    id: int
    type: OrderTypeEnum
    table_id: int | None = None
    created_at: datetime
    paid: bool = False
    paid_online: bool = False

    class Config:
        from_attributes = True


class SOrderFilter(BaseModel):
    paid: bool | None = None
    from_created_date: datetime | None = None
    to_created_date: datetime | None = None
    type: OrderTypeEnum | None = None
    created_by: int | None = None
    paid_by: int | None = None

    class Config:
        extra = 'forbid'

    def to_query_filters(self) -> dict:
        query_filters = {}
        if self.paid is not None:
            query_filters['paid'] = self.paid
        if self.type:
            query_filters['type'] = self.type
        if self.created_by:
            query_filters['created_by'] = self.created_by
        if self.paid_by:
            query_filters['paid_by'] = self.paid_by
        if self.from_created_date:
            query_filters[(Order.created_at, ">=")] = self.from_created_date
        if self.to_created_date:
            query_filters[(Order.created_at, "<=")] = self.to_created_date
        return query_filters


class SOrderItemAddOrEdit(BaseModel):
    quantity: int | None = Field(None, ge=1)

    class Config:
        extra = 'forbid'


class SOrderItemPublicResponse(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    price: Decimal
    type: MenuItemTypeEnum
    weight: int

    class Config:
        from_attributes = True


class SOrderItem(SOrderItemPublicResponse):
    cost: Decimal
