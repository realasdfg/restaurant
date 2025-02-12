from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_jwt_token(data: dict, token_type: str = 'access', expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if token_type == 'access':
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=settings.access_token_expires_hours))
    else:
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.refresh_token_expires_days))
    to_encode.update({'exp': expire, 'type': f'{token_type}'})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def verify_token(token: str, token_type: str | None = None):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if token_type and payload.get('type') != token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
