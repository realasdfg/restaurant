from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.menu import router as menu_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.orders import router as orders_router
from app.services.websockets import router as websockets_router

def create_app():
    app = FastAPI(root_path='/api/v1')
    app.include_router(websockets_router)

    app.include_router(auth_router)
    app.include_router(menu_router)
    app.include_router(users_router)
    app.include_router(orders_router)

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
