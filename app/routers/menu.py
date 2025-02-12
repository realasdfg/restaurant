from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.dependencies import menu_categories_service, menu_items_service
from app.models.users import User
from app.schemas.menu import SMenuItemAdd, SMenuCategory, SMenuItem, SMenuItemEdit, SMenuCategoryAdd, \
    SMenuItemPublicResponse, SMenuItemFilter
from app.schemas.users import RoleEnum
from app.services.menu import MenuCategoriesService, MenuItemsService
from app.utils.roles import get_current_user_if_role, get_current_user_if_role_or_none

router = APIRouter(
    prefix='',
    tags=['Menu']
)


@router.post('/menu-categories')
async def add_menu_category(menu_category: SMenuCategoryAdd,
                            categories_service: MenuCategoriesService = Depends(menu_categories_service),
                            current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuCategory:
    try:
        category = await categories_service.add_menu_category(menu_category)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    return SMenuCategory.model_validate(category)


@router.get('/menu-categories')
async def get_menu_categories(categories_service: MenuCategoriesService =
                              Depends(menu_categories_service)) -> list[SMenuCategory]:
    categories = await categories_service.get_menu_categories()
    return [SMenuCategory.model_validate(cat) for cat in categories]


@router.get('/menu-categories/{category_id}')
async def get_menu_category(category_id: int,
                            categories_service: MenuCategoriesService = Depends(
                                menu_categories_service)) -> SMenuCategory:
    category = await categories_service.get_menu_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return SMenuCategory.model_validate(category)


@router.put('/menu-categories/{category_id}')
async def update_menu_category(category_id: int, menu_category: SMenuCategoryAdd,
                               categories_service: MenuCategoriesService = Depends(menu_categories_service),
                               current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuCategory:
    try:
        category = await categories_service.update_menu_category_by_id(category_id, menu_category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    return SMenuCategory.model_validate(category)


@router.delete('/menu-categories/{category_id}')
async def delete_menu_category(category_id: int,
                               categories_service: MenuCategoriesService = Depends(menu_categories_service),
                               current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> dict:
    try:
        await categories_service.delete_menu_category_by_id(category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": 200, "message": f"Category with id {category_id} deleted"}


@router.post('/menu-items')
async def add_menu_item(menu_item: SMenuItemAdd, items_service: MenuItemsService = Depends(menu_items_service),
                        categories_service: MenuCategoriesService = Depends(menu_categories_service),
                        current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuItem:
    try:
        item = await items_service.add_menu_item(menu_item, categories_service)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Failed to create item due to a database error.')
    return SMenuItem.model_validate(item)


@router.get('/menu-items')
async def get_menu_items(filters: SMenuItemFilter = Depends(),
                         items_service: MenuItemsService = Depends(menu_items_service),
                         current_user: User | None = Depends(
                             get_current_user_if_role_or_none(RoleEnum.ADMIN))) -> (list[SMenuItemPublicResponse] |
                                                                                    list[SMenuItem]):
    items = await items_service.get_menu_items(filters, current_user)
    if current_user is None:
        return [SMenuItemPublicResponse.model_validate(item) for item in items]
    else:
        return [SMenuItem.model_validate(item) for item in items]


@router.get('/menu-items/{item_id}')
async def get_menu_item(item_id: int, items_service: MenuItemsService = Depends(menu_items_service),
                        current_user: User | None = Depends(
                            get_current_user_if_role_or_none(RoleEnum.ADMIN))) -> SMenuItemPublicResponse | SMenuItem:
    item = await items_service.get_menu_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if current_user is None:
        if item.available is False:
            raise HTTPException(status_code=404, detail="Item not found")
        return SMenuItemPublicResponse.model_validate(item)
    else:
        return SMenuItem.model_validate(item)


@router.patch('/menu-items/{item_id}')
async def update_menu_item(item_id: int, menu_item: SMenuItemEdit,
                           items_service: MenuItemsService = Depends(menu_items_service),
                           categories_service: MenuCategoriesService = Depends(menu_categories_service),
                           current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))) -> SMenuItem:
    try:
        item = await items_service.update_menu_item_by_id(item_id, menu_item, categories_service)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return SMenuItem.model_validate(item)


@router.delete('/menu-items/{item_id}')
async def delete_menu_item(item_id: int, items_service: MenuItemsService = Depends(menu_items_service),
                           current_user: User = Depends(get_current_user_if_role(RoleEnum.ADMIN))):
    try:
        await items_service.delete_menu_item_by_id(item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": 200, "message": f"Item with id {item_id} deleted"}
