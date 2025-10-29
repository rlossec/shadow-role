from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.user import User
from schemas.user import UserCreate


class UserRepository:
    """Repository pour la gestion des utilisateurs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ❌ SYNC (bloquant)
    # async def get_user(self, user_id: int):
    #     result = self.db.query(User).filter(User.id == user_id).first()
    #     # Ici, le thread attend que la base de données réponde...
    #     # Pendant ce temps, il ne peut rien faire d'autre
    #     return result
    
    # ✅ ASYNC (non-bloquant)
    async def get_user(self, user_id: int) -> User | None:
        """Récupère un utilisateur par son ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> User | None:
        """Récupère un utilisateur par son email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        """Crée un nouvel utilisateur"""
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Récupère tous les utilisateurs avec pagination"""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

