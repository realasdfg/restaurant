from pydantic import BaseModel, Field


class STableAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)

    class Config:
        extra = 'forbid'


class STable(STableAdd):
    id: int
    is_free: bool = True
    is_deleted: bool = False

    class Config:
        from_attributes = True
