from fastapi import FastAPI

from app.routers.menu import router as menu_router

def create_app():
    app = FastAPI(root_path='/api/v1')
    app.include_router(menu_router)
    return app
