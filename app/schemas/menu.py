from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import MenuItemTypeEnum


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
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=256)
    price: Decimal = Field(..., ge=0)
    cost: Decimal = Field(..., ge=0)
    type: MenuItemTypeEnum
    weight: int = Field(..., ge=1)
    available: bool = True
    category_id: int


class SMenuItemEdit(SMenuItemAdd):
    name: str = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=256)
    price: Decimal = Field(None, ge=0)
    cost: Decimal = Field(None, ge=0)
    type: MenuItemTypeEnum = None
    weight: int = Field(None, ge=1)
    available: bool = None
    category_id: int = None


class SMenuItem(SMenuItemAdd):
    id: int
    image: str | None = None
    is_deleted: bool = False

    class Config:
        from_attributes = True


class SMenuItemPublicResponse(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=256)
    image: str | None = None
    price: Decimal = Field(..., ge=0)
    type: MenuItemTypeEnum
    weight: int = Field(..., ge=1)
    available: bool = True
    category_id: int

    class Config:
        from_attributes = True


class SMenuItemFilter(BaseModel):
    available: bool | None = None
