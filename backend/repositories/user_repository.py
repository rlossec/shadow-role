from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import PasswordResetToken, User, VerificationToken
from db.schemas import UserCreate, UserUpdate
from utils.password_hashing import hash_password


class UserRepository:
    """Repository for the user model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination"""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_user(self, user_id: UUID) -> User | None:
        """Get a user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_user_by_identifier(self, identifier: str) -> User | None:
        """Get a user by username OR email (case-insensitive)."""
        lowered = identifier.lower()
        result = await self.db.execute(
            select(User).where(func.lower(User.username) == lowered)
        )
        user = result.scalar_one_or_none()
        if user:
            return user

        result = await self.db.execute(
            select(User).where(func.lower(User.email) == lowered)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def username_exists(self, username: str) -> bool:
        result = await self.db.execute(
            select(func.count(User.id)).where(func.lower(User.username) == username.lower())
        )
        return (result.scalar() or 0) > 0

    async def email_exists(self, email: str) -> bool:
        result = await self.db.execute(
            select(func.count(User.id)).where(func.lower(User.email) == email.lower())
        )
        return (result.scalar() or 0) > 0
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update a user"""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user"""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        await self.db.delete(user)
        await self.db.commit()

    async def set_user_password(self, user_id: UUID, password: str) -> None:
        """Set a user's password"""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        user.hashed_password = hash_password(password)
        await self.db.commit()
        await self.db.refresh(user)

    async def set_user_verified(self, user_id: UUID) -> None:
        """Set a user's verified status"""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)

    async def set_user_active(self, user_id: UUID, is_active: bool) -> None:
        """Set a user's active status"""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        user.is_active = is_active
        await self.db.commit()
        await self.db.refresh(user)

    # --- Méthodes PasswordResetToken ---

    async def create_password_reset_token(self, user_id: UUID, token: str, expires_at: datetime) -> PasswordResetToken:
        # D'abord, supprimer les anciens tokens non utilisés pour cet utilisateur
        await self.db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id, PasswordResetToken.used.is_(False))
        )
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self.db.add(reset_token)
        await self.db.commit()
        return reset_token

    async def get_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        result = await self.db.execute(select(PasswordResetToken).where(PasswordResetToken.token == token))
        return result.scalar_one_or_none()

    async def mark_reset_token_used(self, token_id: UUID) -> None:
        await self.db.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(used=True, expires_at=datetime.now(timezone.utc)) # Marquer comme utilisé
        )
        await self.db.commit()

    # --- Méthodes VerificationToken ---

    async def create_verification_token(self, user_id: UUID, token: str, expires_at: datetime) -> VerificationToken:
        await self.db.execute(
            delete(VerificationToken).where(VerificationToken.user_id == user_id, VerificationToken.used.is_(False))
        )

        verification_token = VerificationToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self.db.add(verification_token)
        await self.db.commit()
        return verification_token

    async def get_verification_token(self, token: str) -> Optional[VerificationToken]:
        result = await self.db.execute(select(VerificationToken).where(VerificationToken.token == token))
        return result.scalar_one_or_none()

    async def mark_verification_token_used(self, token_id: UUID) -> None:
        await self.db.execute(
            update(VerificationToken)
            .where(VerificationToken.id == token_id)
            .values(used=True, expires_at=datetime.now(timezone.utc))
        )
        await self.db.commit()