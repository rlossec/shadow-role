from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from core.config import settings
from models import PasswordResetToken, User, AccountActivationToken
from repositories.user_repository import UserRepository

from utils.normalize_datetime import normalize_datetime


class PasswordResetManager:
    """Handle issuance and validation of password reset tokens."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def create_token(self, user: User) -> str:
        token = secrets.token_urlsafe(48)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.RESET_TOKEN_EXPIRATION_HOURS)
        await self.user_repository.create_password_reset_token(user.id, token, expires_at)
        return token

    async def verify_token(self, token: str) -> Optional[PasswordResetToken]:
        reset_token = await self.user_repository.get_password_reset_token(token)
        if reset_token is None:
            return None
        if reset_token.used:
            return None
        if normalize_datetime(reset_token.expires_at) < datetime.now(timezone.utc):
            return None
        return reset_token

    async def mark_token_used(self, token: PasswordResetToken) -> None:
        await self.user_repository.mark_reset_token_used(token.id)


class AccountActivationTokenManager:
    """Handle issuance and validation of email account activation tokens."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def create_token(self, user: User) -> str:
        token = secrets.token_urlsafe(48)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.ACCOUNT_ACTIVATION_TOKEN_EXPIRATION_HOURS)
        await self.user_repository.create_account_activation_token(user.id, token, expires_at)
        return token

    async def verify_token(self, token: str) -> Optional[AccountActivationToken]:
        account_activation_token = await self.user_repository.get_account_activation_token(token)
        if account_activation_token is None:
            return None
        if account_activation_token.used:
            return None
        if normalize_datetime(account_activation_token.expires_at) < datetime.now(timezone.utc):
            return None
        return account_activation_token

    async def mark_token_used(self, token: AccountActivationToken) -> None:
        await self.user_repository.mark_account_activation_token_used(token.id)
