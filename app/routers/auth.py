from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.auth import get_user_by_username, create_jwt_token, get_password_hash, verify_password, verify_token
from app.database import get_async_session
from app.models.users import User
from app.schemas.auth import SUserLogin, SUserRegister, SUserLoginResponse, SToken
from app.schemas.users import SUserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register(user: SUserRegister = Depends(), session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).filter(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, first_name=user.first_name, last_name=user.last_name, role=user.role,
                    password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return SUserResponse.model_validate(new_user, from_attributes=True)


@router.post("/login")
async def login(user_data: SUserLogin = Depends(), session: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_username(user_data.username, session)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if not verify_password(user_data.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await create_jwt_token(data={"sub": user.username}, token_type='access')
    refresh_token = await create_jwt_token(data={"sub": user.username}, token_type='refresh')
    await session.commit()
    response = SUserLoginResponse.model_validate(user, from_attributes=True)
    response.access_token = access_token
    response.refresh_token = refresh_token
    response.token_type = 'Bearer'
    return response


@router.post("/token/refresh")
async def token_refresh(refresh_token: str | None = None):
    payload = await verify_token(refresh_token, "refresh")
    user_username: str = payload.get("sub")
    if user_username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    new_access_token = await create_jwt_token(data={"sub": user_username}, token_type='access')
    new_refresh_token = await create_jwt_token(data={"sub": user_username}, token_type='refresh')
    return SToken(access_token=new_access_token, refresh_token=new_refresh_token, token_type="Bearer")
