from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import AuthRouter
from app.routers.menu import MenuItemsRouter, MenuCategoriesRouter
from app.routers.users import UsersRouter
from app.routers.tables import TablesRouter
from app.routers.orders import OrdersRouter
from app.routers.websockets import WebsocketRouter

def create_app():
    app = FastAPI(root_path='/api/v1')
    app.include_router(WebsocketRouter().router)

    app.include_router(AuthRouter().router)
    app.include_router(MenuItemsRouter().router)
    app.include_router(MenuCategoriesRouter().router)
    app.include_router(UsersRouter().router)
    app.include_router(TablesRouter().router)
    app.include_router(OrdersRouter().router)

    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
