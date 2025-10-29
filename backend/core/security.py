# backend/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWTError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserResponse
from repositories.user_repository import UserRepository
from core.database import get_db

from core.config import settings
from core.password import verify_password

# --- constants / settings ---

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- JWT token creation / vérification ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def decode_access_token_optional_expiry(token: str) -> dict:
    """Decode token without checking expiry - used for refresh"""
    try:
        # decode without verifying expiry
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# --- FastAPI dependencies to get the current user ---

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user_repository = UserRepository(db)
    user_in_db = await user_repository.get_user(user_id)
    if not user_in_db:
        raise credentials_exception
    
    return UserResponse.model_validate(user_in_db)

async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def authenticate_user(
    username: str, 
    password: str, 
    db: AsyncSession
) -> UserResponse | None:
    user_repository = UserRepository(db)
    user_in_db = await user_repository.get_user_by_username(username)
    if not user_in_db:
        return None
    if not verify_password(password, user_in_db.hashed_password):
        return None
    # Vérifier que l'utilisateur est actif
    if not user_in_db.is_active:
        return None
    user = UserResponse.model_validate(user_in_db)
    return user
