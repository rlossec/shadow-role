
from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.schemas import RoundCreate
from app.models.round import Round, RoundStatus

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
    
    async def get_current_running_round(self, lobby_id: UUID) -> Optional[Round]:
        """
        Obtenir le round actuel d'un lobby (status = RUNNING).
        
        Returns:
            Le round en cours s'il existe, None sinon.
            En cas de plusieurs rounds RUNNING, retourne le plus récent (round_number le plus élevé).
        """
        result = await self.db.execute(
            select(Round).where(
                and_(
                    Round.lobby_id == lobby_id,
                    Round.status == RoundStatus.RUNNING
                )
            ).order_by(Round.round_number.desc()).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def create_round(self, round_data: RoundCreate) -> Round:
        """Create a new round"""
        round = Round(**round_data.model_dump())
        self.db.add(round)
        await self.db.commit()
        await self.db.refresh(round)
        return round