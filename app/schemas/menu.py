from pydantic import BaseModel

class MenuCategorySchema(BaseModel):
    name: str

class MenuItemSchema(BaseModel):
    name: str
    category: int