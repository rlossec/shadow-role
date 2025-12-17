
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas import RoundCreate
from models.round import Round

class RoundRepository:
    """Repository for the round model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_round(self, round_id: UUID) -> Round | None:
        """Get a round by ID"""
        result = await self.db.execute(select(Round).where(Round.id == round_id))
        return result.scalar_one_or_none()
    
    async def get_round_by_lobby_and_number(self, lobby_id: UUID, round_number: int) -> Round | None:
        """Get a round by lobby ID and round number"""
        result = await self.db.execute(
            select(Round).where(
                Round.lobby_id == lobby_id,
                Round.round_number == round_number
            )
        )
        return result.scalar_one_or_none()
    
    async def create_round(self, round_data: RoundCreate) -> Round:
        """Create a new round"""
        round = Round(**round_data.model_dump())
        self.db.add(round)
        await self.db.commit()
        await self.db.refresh(round)
        return round