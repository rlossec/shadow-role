from __future__ import annotations

import uuid
from typing import Optional

from fastapi import HTTPException, status

from core.config import settings
from db.schemas.user import UserCreate
from models import User
from repositories.jwt_repository import JWTRepository
from repositories.user_repository import UserRepository
from utils.password_hashing import verify_password


class AuthenticationService:
    """Coordinate user registration, authentication and JWT issuance."""

    def __init__(self, user_repository: UserRepository, jwt_repository: JWTRepository) -> None:
        self.user_repository = user_repository
        self.jwt_repository = jwt_repository

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

    async def set_user_verified(self, user_id: uuid.UUID | str) -> None:
        parsed = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        await self.user_repository.set_user_verified(parsed)

    def create_token_pair(self, user_id: uuid.UUID) -> tuple[str, str]:
        access = self.jwt_repository.create_access_token(user_id)
        refresh = self.jwt_repository.create_refresh_token(user_id)
        return access, refresh

    def create_access_token(self, user_id: uuid.UUID) -> str:
        return self.jwt_repository.create_access_token(user_id)

    def extract_user_id_from_refresh_token(self, token: str) -> uuid.UUID:
        return self.jwt_repository.extract_user_id_from_refresh_token(token)

    def decode_token(self, token: str) -> dict:
        return self.jwt_repository.decode_token(token)


def build_authentication_service(user_repository: UserRepository) -> AuthenticationService:
    jwt_repository = JWTRepository(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return AuthenticationService(user_repository, jwt_repository)
