from pydantic import BaseModel


class MenuItemSchema(BaseModel):
    name: str
    category: int