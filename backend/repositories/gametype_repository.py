
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import GameType
from schemas import GameTypeCreate, GameTypeUpdate


class GameTypeRepository:
    """Repository for the game type model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_game_types(self) -> list[GameType]:
        """Get all game types"""
        result = await self.db.execute(select(GameType))
        return list(result.scalars().all())
    
    async def get_game_type(self, game_type_id: UUID) -> GameType | None:
        """Get a game type by ID"""
        result = await self.db.execute(select(GameType).where(GameType.id == game_type_id))
        return result.scalar_one_or_none()
      
    async def get_game_type_by_name(self, name: str) -> GameType | None:
        """Get a game type by name"""
        result = await self.db.execute(select(GameType).where(GameType.name == name))
        return result.scalar_one_or_none()

    async def create_game_type(self, game_type_data: GameTypeCreate) -> GameType:
        """Create a new game type"""
        game_type = GameType(**game_type_data.model_dump())
        self.db.add(game_type)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(game_type)
        return game_type

    async def update_game_type(self, game_type_id: UUID, game_type_data: GameTypeUpdate) -> GameType:
        """Update a game type"""
        game_type = await self.get_game_type(game_type_id)
        if game_type:
            for field, value in game_type_data.model_dump(exclude_unset=True).items():
                setattr(game_type, field, value)
            await self.db.commit()
            await self.db.refresh(game_type)
            return game_type
        return None

    async def delete_game_type(self, game_type_id: UUID) -> bool:
        """Delete a game type"""
        game_type = await self.get_game_type(game_type_id)
        if game_type:
            await self.db.delete(game_type)
            await self.db.commit()
            return True
        return False