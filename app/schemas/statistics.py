from datetime import datetime, time

from fastapi import HTTPException
from pydantic import BaseModel, model_validator, field_validator

from app.models.enums import OrderTypeEnum


class SOrdersRevenue(BaseModel):
    from_date: datetime
    to_date: datetime
    type: OrderTypeEnum | None = None
    # paid_by_card_only: bool | None = None
    # paid_by_cash_only: bool | None = None
    # paid_online_only: bool | None = None
    category_id: int | None = None
    period: str | None = None

    class Config:
        extra = 'forbid'

    @model_validator(mode='after')
    def validate(self):
        if self.from_date > self.to_date:
            raise HTTPException(status_code=422, detail="from_date should be earlier than to_date")
        if self.period not in ['daily', 'weekly', 'monthly']:
            raise HTTPException(status_code=422, detail="Invalid period. Allowed values: daily, weekly, monthly.")
        # if self.paid_by_card_only and self.paid_by_cash_only:
        #     raise HTTPException(status_code=422, detail="paid_by_card_only and paid_by_cash_only cannot both be true")
        return self

    @field_validator("to_date")
    @classmethod
    def adjust_to_date(cls, value: datetime) -> datetime:
        if value.time() == time.min:
            return datetime.combine(value.date(), time.max)
        return value
