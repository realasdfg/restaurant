import enum


class OrderTypeEnum(enum.Enum):
    DINEIN = "dinein"
    TOGO = "togo"


class MenuItemTypeEnum(enum.Enum):
    BY_WEIGHT = "by_weight"
    BY_QUANTITY = "by_quantity"


class RoleEnum(enum.Enum):
    STAFF = "staff"
    ADMIN = "admin"
