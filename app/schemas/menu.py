from pydantic import BaseModel


class MenuCategorySchema(BaseModel):
    name: str


class MenuCategoryResponse(BaseModel):
    id: int
    name: str


class MenuItemSchema(BaseModel):
    name: str
    category: int
