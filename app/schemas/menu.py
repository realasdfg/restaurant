from decimal import Decimal

from pydantic import BaseModel, Field


class SMenuCategory(BaseModel):
    name: str


class SMenuCategoryResponse(SMenuCategory):
    id: int


class SMenuItem(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    image: str | None = None
    price: Decimal
    cost: Decimal
    available: bool = True
    category_id: int


class SMenuItemResponse(SMenuItem):
    id: int
