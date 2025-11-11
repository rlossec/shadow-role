from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Any

from fastapi import HTTPException, status

from core.config import settings
from db.schemas.user import UserCreate
from models import User
from repositories.jwt_repository import JWTRepository
from repositories.token_repository import TokenRepository
from repositories.user_repository import UserRepository
from services.notifications.interface import NotificationService
from .link_builder import NotificationLinkBuilder
from utils.password_hashing import verify_password


class AuthenticationService:
    """Coordinate user registration, authentication and JWT issuance."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        jwt_repository: JWTRepository,
        notification_service: NotificationService | None = None,
        link_builder: NotificationLinkBuilder | None = None,
    ) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.jwt_repository = jwt_repository
        self.notification_service = notification_service or _NullNotificationService()
        self.link_builder = link_builder or NotificationLinkBuilder()

    async def register_user(self, user_create: UserCreate) -> User:
        if await self.user_repository.username_exists(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        if await self.user_repository.email_exists(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
        return await self.user_repository.create_user(user_create)

    async def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_user_by_identifier(identifier)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_id(self, user_id: uuid.UUID | str) -> Optional[User]:
        try:
            parsed = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except (TypeError, ValueError):
            return None
        return await self.user_repository.get_user(parsed)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repository.get_user_by_email(email)

    async def set_user_password(self, user_id: uuid.UUID | str, new_password: str) -> None:
        parsed = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        await self.user_repository.set_user_password(parsed, new_password)

    async def set_user_active(self, user_id: uuid.UUID | str, is_active: bool) -> None:
        parsed = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        await self.user_repository.set_user_active(parsed, is_active)

    def create_token_pair(self, user_id: uuid.UUID) -> tuple[str, str]:
        access = self.jwt_repository.create_access_token(user_id)
        refresh = self.jwt_repository.create_refresh_token(user_id)
        return access, refresh

    def create_access_token(self, user_id: uuid.UUID) -> str:
        return self.jwt_repository.create_access_token(user_id)

    def _decode_refresh_token(self, token: str) -> dict:
        payload = self.jwt_repository.decode_refresh_token(token)
        if payload.get("jti") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalide (jti manquant)",
            )
        return payload

    async def _ensure_refresh_token_not_revoked(self, jti: str, user_id: uuid.UUID) -> None:
        if await self.token_repository.is_refresh_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token révoqué",
            )

    async def extract_user_id_from_refresh_token(self, token: str) -> uuid.UUID:
        payload = self._decode_refresh_token(token)
        try:
            user_id = uuid.UUID(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide (sub)",
            ) from exc

        await self._ensure_refresh_token_not_revoked(payload["jti"], user_id)
        return user_id

    async def rotate_refresh_token(self, token: str) -> tuple[str, str]:
        payload = self._decode_refresh_token(token)
        try:
            user_id = uuid.UUID(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide (sub)",
            ) from exc

        await self._ensure_refresh_token_not_revoked(payload["jti"], user_id)

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        access_token, refresh_token = self.create_token_pair(user.id)

        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        await self.token_repository.revoke_refresh_token(
            jti=payload["jti"],
            user_id=user.id,
            expires_at=expires_at,
            reason="rotated",
        )

        return access_token, refresh_token

    async def revoke_refresh_token(self, token: str, reason: str = "logout") -> None:
        payload = self._decode_refresh_token(token)
        try:
            user_id = uuid.UUID(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide (sub)",
            ) from exc

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        await self.token_repository.revoke_refresh_token(
            jti=payload["jti"],
            user_id=user.id,
            expires_at=expires_at,
            reason=reason,
        )

    def decode_token(self, token: str) -> dict:
        return self.jwt_repository.decode_token(token)


    async def notify_account_activation(self, user: User, token: str) -> None:
        activation_link = self.link_builder.build_activation_link(user.id, token)
        context = {
            "username": user.username,
            "activation_link": activation_link,
        }
        await self.notification_service.send(
            to=user.email,
            template_name="auth_activation",
            context=context,
        )

    async def notify_activation_confirmation(self, user: User) -> None:
        context = {
            "username": user.username,
        }
        await self.notification_service.send(
            to=user.email,
            template_name="auth_activation_confirmation",
            context=context,
        )

    async def notify_password_reset(self, user: User, token: str) -> None:
        reset_link = self.link_builder.build_reset_password_link(user.id, token)
        context = {
            "username": user.username,
            "reset_link": reset_link,
        }
        await self.notification_service.send(
            to=user.email,
            template_name="auth_password_reset",
            context=context,
        )


class _NullNotificationService(NotificationService):
    async def send(self, to: str, template_name: str, context: dict[str, Any]) -> None:  # noqa: D401
        return None


def build_authentication_service(
    user_repository: UserRepository,
    token_repository: Optional[TokenRepository] = None,
    notification_service: NotificationService | None = None,
    link_builder: NotificationLinkBuilder | None = None,
) -> AuthenticationService:
    jwt_repository = JWTRepository(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    token_repo = token_repository or TokenRepository(user_repository.db)
    return AuthenticationService(
        user_repository,
        token_repo,
        jwt_repository,
        notification_service=notification_service,
        link_builder=link_builder,
    )
