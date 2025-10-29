from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from schemas import UserCreate, UserUpdate
from core.password import get_password_hash


class UserRepository:
    """Repository for the user model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination"""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_user(self, user_id: int) -> User | None:
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
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
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

