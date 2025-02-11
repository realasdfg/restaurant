from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.menu import MenuCategory, MenuItem
from app.models.users import User
from app.schemas.menu import SMenuItemAdd, SMenuCategory, SMenuItem, SMenuItemEdit, SMenuCategoryAdd
from app.schemas.users import RoleEnum
from app.services.roles import get_current_user_if_role

router = APIRouter(
    prefix='',
    tags=['Menu']
)


@router.post('/menu-categories')
async def add_menu_category(menu_category: SMenuCategoryAdd,
                            session: AsyncSession = Depends(get_async_session),
                            current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuCategory:
    new_category = MenuCategory(name=menu_category.name)
    session.add(new_category)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Category already exists")
    return SMenuCategory.model_validate(new_category, from_attributes=True)


@router.get('/menu-categories')
async def get_menu_categories(session: AsyncSession = Depends(get_async_session)) -> list[SMenuCategory]:
    result = await session.execute(select(MenuCategory))
    categories = result.scalars().all()
    return [SMenuCategory.model_validate(cat, from_attributes=True) for cat in categories]


@router.get('/menu-categories/{category_id}')
async def get_menu_category(category_id: int,
                            session: AsyncSession = Depends(get_async_session)) -> SMenuCategory:
    result = await session.execute(select(MenuCategory).where(MenuCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return SMenuCategory.model_validate(category, from_attributes=True)


@router.put('/menu-categories/{category_id}')
async def update_menu_category(category_id: int,
                               menu_category: SMenuCategoryAdd,
                               session: AsyncSession = Depends(get_async_session),
                               current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuCategory:
    result = await session.execute(select(MenuCategory).where(MenuCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = menu_category.name
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Category already exists")
    return SMenuCategory.model_validate(category, from_attributes=True)


@router.delete('/menu-categories/{category_id}')
async def delete_menu_category(category_id: int, session: AsyncSession = Depends(get_async_session),
                               current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
    result = await session.execute(select(MenuCategory).where(MenuCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(category)
    await session.commit()
    return {"status": 200, "message": "Category deleted"}


@router.get('/menu-categories/{category_id}/menu-items')
async def get_menu_items_by_category(category_id: int, session: AsyncSession = Depends(get_async_session),
                                     current_user: User = Depends(get_current_user_if_role(RoleEnum.STAFF))) -> list[
    SMenuItem]:
    result = await session.execute(select(MenuItem).where(MenuItem.category_id == category_id))
    items = result.scalars().all()
    return [SMenuItem.model_validate(item, from_attributes=True) for item in items]


@router.post('/menu-items')
async def add_menu_item(menu_item: SMenuItemAdd,
                        session: AsyncSession = Depends(get_async_session),
                        current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuItem:
    existing_item_query = select(MenuItem).where(MenuItem.name == menu_item.name)
    result = await session.execute(existing_item_query)
    existing_item = result.scalar_one_or_none()
    if existing_item:
        raise HTTPException(status_code=400, detail="Item with this name already exists.")

    category_query = select(MenuCategory).where(MenuCategory.id == menu_item.category_id)
    category_result = await session.execute(category_query)
    category = category_result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category with this ID does not exist.")

    new_item = MenuItem(
        name=menu_item.name,
        description=menu_item.description,
        image=menu_item.image,
        price=menu_item.price,
        cost=menu_item.cost,
        type=menu_item.type,
        weight=menu_item.weight,
        available=menu_item.available,
        category_id=menu_item.category_id
    )
    session.add(new_item)
    try:
        await session.commit()
        await session.refresh(new_item)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Failed to create item due to a database error.")
    return SMenuItem.model_validate(new_item, from_attributes=True)


@router.get('/menu-items')
async def get_menu_items(session: AsyncSession = Depends(get_async_session)) -> list[SMenuItem]:
    query = select(MenuItem)
    result = await session.execute(query)
    items = result.scalars().all()
    return [SMenuItem.model_validate(item, from_attributes=True) for item in items]


@router.get('/menu-items/{item_id}')
async def get_menu_item(item_id: int, session: AsyncSession = Depends(get_async_session)) -> SMenuItem:
    result = await session.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return SMenuItem.model_validate(item, from_attributes=True)


@router.patch('/menu-items/{item_id}')
async def update_menu_item(item_id: int,
                           menu_item: SMenuItemEdit,
                           session: AsyncSession = Depends(get_async_session),
                           current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuItem:
    result = await session.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if menu_item.name:
        item.name = menu_item.name
    if menu_item.description:
        item.description = menu_item.description
    if menu_item.image:
        item.image = menu_item.image
    if menu_item.price:
        item.price = menu_item.price
    if menu_item.cost:
        item.cost = menu_item.cost
    if menu_item.type:
        item.type = menu_item.type
    if menu_item.weight:
        item.weight = menu_item.weight
    if menu_item.available:
        item.available = menu_item.available
    if menu_item.category_id:
        result = await session.execute(select(MenuCategory).where(MenuCategory.id == menu_item.category_id))
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        item.category_id = menu_item.category_id
    await session.commit()
    return SMenuItem.model_validate(item, from_attributes=True)


@router.delete('/menu-items/{item_id}')
async def delete_menu_item(item_id: int, session: AsyncSession = Depends(get_async_session),
                           current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
    result = await session.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(item)
    await session.commit()
    return {"status": 200, "message": "Item deleted"}
