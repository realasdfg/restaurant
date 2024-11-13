import uvicorn

from app import create_app

if __name__ == '__main__':
    uvicorn.run(create_app(), host='localhost', port=8000, reload=True)