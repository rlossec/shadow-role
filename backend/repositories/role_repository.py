from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from models import Role


class RoleRepository:
    """Repository for the role model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_role(self, role_id: UUID) -> Role | None:
        """Get a role by ID"""
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()
    
    async def get_roles_by_game(self, game_id: UUID) -> list[Role]:
        """Get all roles for a game"""
        result = await self.db.execute(
            select(Role).where(Role.game_id == game_id)
        )
        return list(result.scalars().all())
    
    async def get_roles_with_relations(self, game_id: UUID) -> list[Role]:
        """Get all roles for a game with missions loaded"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.missions))
            .where(Role.game_id == game_id)
        )
        return list(result.scalars().all())

