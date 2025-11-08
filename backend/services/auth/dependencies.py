from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.database import get_async_session
from db.schemas.user import UserResponse
from repositories.user_repository import UserRepository

from .service import AuthenticationService, build_authentication_service
from .token_manager import PasswordResetManager, VerificationTokenManager


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/jwt/login")


async def get_authentication_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthenticationService:
    user_repo = UserRepository(session)
    return build_authentication_service(user_repo)


async def get_password_reset_manager(
    session: AsyncSession = Depends(get_async_session),
) -> PasswordResetManager:
    user_repo = UserRepository(session)
    return PasswordResetManager(user_repo)


async def get_verification_manager(
    session: AsyncSession = Depends(get_async_session),
) -> VerificationTokenManager:
    user_repo = UserRepository(session)
    return VerificationTokenManager(user_repo)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> UserResponse:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = auth_service.decode_token(token)
        if payload.get("type") != "access":
            raise credentials_error
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_error
        parsed_id = uuid.UUID(str(user_id))
    except Exception as exc:  # pragma: no cover - defensive
        raise credentials_error from exc

    user = await auth_service.get_user_by_id(parsed_id)
    if user is None or not user.is_active:
        raise credentials_error

    return UserResponse.model_validate(user)


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
