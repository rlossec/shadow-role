from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from models.game import Game
from db.schemas import GameCreate


class GameRepository:
    """Repository for the game model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_games(self, skip: int = 0, limit: int = 100) -> list[Game]:
        """Get all games with pagination"""
        result = await self.db.execute(
            select(Game).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_game(self, game_id: UUID) -> Game | None:
        """Get a game by ID"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        return result.scalar_one_or_none()
    
    async def get_game_with_relations(self, game_id: UUID) -> Game | None:
        """Get a game with roles and missions"""
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.roles), selectinload(Game.missions))
            .where(Game.id == game_id)
        )
        return result.scalar_one_or_none()
    
    async def create_game(self, game_data: GameCreate) -> Game:
        """Create a new game"""
        game = Game(**game_data.model_dump())
        self.db.add(game)
        await self.db.commit()
        await self.db.refresh(game)
        return game

