import enum
from decimal import Decimal

from pydantic import BaseModel, Field

class MenuItemTypeEnum(enum.Enum):
    BY_WEIGHT = "by_weight"
    BY_QUANTITY = "by_quantity"

class SMenuCategory(BaseModel):
    name: str = Field(..., max_length=50)


class SMenuCategoryResponse(SMenuCategory):
    id: int


class SMenuItem(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    image: str | None = None
    price: Decimal
    cost: Decimal
    # type: # str = mapped_column(Enum('by_weight', 'by_quantity', name='menuitem_type'))
    available: bool = True
    category_id: int


class SMenuItemEdit(SMenuItem):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    image: str | None = None
    price: Decimal | None = None
    cost: Decimal | None = None
    available: bool | None = None
    category_id: int | None = None


class SMenuItemResponse(SMenuItem):
    id: int
