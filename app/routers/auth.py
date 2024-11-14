from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.users import User
from app.schemas.users import SUserResponse, SUserRegister

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
    new_user = User(username=user.username, first_name=user.first_name, last_name=user.last_name, role=user.role)
    new_user.set_password(user.password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return SUserResponse.model_validate(new_user, from_attributes=True)
