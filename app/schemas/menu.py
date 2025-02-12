import enum
from decimal import Decimal

from pydantic import BaseModel, Field


class MenuItemTypeEnum(enum.Enum):
    BY_WEIGHT = "by_weight"
    BY_QUANTITY = "by_quantity"


class SMenuCategoryAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

    class Config:
        extra = 'forbid'


class SMenuCategory(SMenuCategoryAdd):
    id: int
    is_deleted: bool = False

    class Config:
        from_attributes = True


class SMenuItemAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    image: str | None = None
    price: Decimal = Field(..., ge=0)
    cost: Decimal = Field(..., ge=0)
    type: MenuItemTypeEnum
    weight: int
    available: bool = True
    category_id: int

    class Config:
        extra = 'forbid'


class SMenuItemEdit(SMenuItemAdd):
    name: str = Field(None, min_length=1, max_length=100)
    description: str | None = None
    image: str | None = None
    price: Decimal = Field(None, ge=0)
    cost: Decimal = Field(None, ge=0)
    type: MenuItemTypeEnum = None
    weight: int = None
    available: bool = None
    category_id: int = None


class SMenuItem(SMenuItemAdd):
    id: int
    is_deleted: bool = False

    class Config:
        from_attributes = True


class SMenuItemPublicResponse(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    image: str | None = None
    price: Decimal
    type: MenuItemTypeEnum
    weight: int
    available: bool = True
    category_id: int

    class Config:
        from_attributes = True


class SMenuItemFilter(BaseModel):
    available: bool | None = None
