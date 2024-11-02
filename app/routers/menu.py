from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.menu import MenuCategory
from app.schemas.menu import MenuItemSchema, MenuCategorySchema, MenuCategoryResponse

router = APIRouter(
    prefix='/menu',
    tags=['Menu']
)

menu_list = []


@router.post('/categories')
async def add_category(menu_category: MenuCategorySchema = Depends(),
                       session: AsyncSession = Depends(get_async_session)) -> MenuCategoryResponse:
    new_category = MenuCategory(name=menu_category.name)
    session.add(new_category)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Category already exists")
    return MenuCategoryResponse.model_validate(new_category, from_attributes=True)

@router.get('/categories')
async def get_categories(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(MenuCategory))
    categories = result.scalars().all()
    return [MenuCategoryResponse.model_validate(cat, from_attributes=True) for cat in categories]


@router.post('/')
async def add_menu_item(menu_item: MenuItemSchema,
                        session: AsyncSession = Depends(get_async_session)):
    session.add(menu_item)
    await session.commit()
    return {"message": "Menu item added successfully"}


@router.get('/')
async def menu():
    return menu_list
