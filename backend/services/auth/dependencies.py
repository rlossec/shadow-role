from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from db.schemas.user import UserResponse
from repositories.user_repository import UserRepository
from repositories.token_repository import TokenRepository
from services.notifications.dependencies import get_notification_service as get_notification_service_dependency
from services.notifications.interface import NotificationService
from .service import AuthenticationService, build_authentication_service
from .token_manager import PasswordResetManager, AccountActivationTokenManager
from .link_builder import NotificationLinkBuilder


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/jwt/login")


def get_link_builder() -> NotificationLinkBuilder:
    return NotificationLinkBuilder()


async def get_authentication_service(
    session: AsyncSession = Depends(get_async_session),
    notification_service: NotificationService = Depends(get_notification_service_dependency),
    link_builder: NotificationLinkBuilder = Depends(get_link_builder),
) -> AuthenticationService:
    user_repo = UserRepository(session)
    token_repo = TokenRepository(session)
    return build_authentication_service(
        user_repo,
        token_repo,
        notification_service=notification_service,
        link_builder=link_builder,
    )


async def get_password_reset_manager(
    session: AsyncSession = Depends(get_async_session),
) -> PasswordResetManager:
    user_repo = UserRepository(session)
    return PasswordResetManager(user_repo)


async def get_account_activation_manager(
    session: AsyncSession = Depends(get_async_session),
) -> AccountActivationTokenManager:
    user_repo = UserRepository(session)
    return AccountActivationTokenManager(user_repo)
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
