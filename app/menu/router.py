from fastapi import APIRouter

from app.menu.schemas import MenuItemSchema

router = APIRouter(
    prefix='/menu',
    tags=['Menu']
)

menu_list = []

@router.post('/')
async def add_menu_item(menu_item: MenuItemSchema):
    menu_list.append(menu_item)
    return {"message": "Menu item added successfully"}

@router.get('/')
async def menu():
    return menu_list