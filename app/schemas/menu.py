import enum
from decimal import Decimal

from pydantic import BaseModel, Field


class MenuItemTypeEnum(enum.Enum):
    BY_WEIGHT = "by_weight"
    BY_QUANTITY = "by_quantity"


class SMenuCategoryAdd(BaseModel):
    name: str = Field(..., max_length=50)


class SMenuCategory(SMenuCategoryAdd):
    id: int
    is_deleted: bool = False


class SMenuItemAdd(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    image: str | None = None
    price: Decimal
    cost: Decimal
    type: MenuItemTypeEnum
    weight: int
    available: bool = True
    category_id: int


class SMenuItemEdit(SMenuItemAdd):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    image: str | None = None
    price: Decimal | None = None
    cost: Decimal | None = None
    type: MenuItemTypeEnum | None = None
    weight: int | None = None
    available: bool | None = None
    category_id: int | None = None


class SMenuItem(SMenuItemAdd):
    id: int
    is_deleted: bool = False
