from datetime import datetime, time

from fastapi import HTTPException
from pydantic import BaseModel, model_validator, field_validator


class SOrdersRevenue(BaseModel):
    from_date: datetime
    to_date: datetime

    class Config:
        extra = 'forbid'

    @model_validator(mode='after')
    def check_dates(self):
        if self.from_date > self.to_date:
            raise HTTPException(status_code=422, detail="from_date should be earlier than to_date")
        return self

    @field_validator("to_date")
    @classmethod
    def adjust_to_date(cls, value: datetime) -> datetime:
        if value.time() == time.min:
            return datetime.combine(value.date(), time.max)
        return value
