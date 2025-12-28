from uuid import UUID
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.schemas import MissionCreate, MissionUpdate
from app.models import Mission, MissionAssigned, MissionAssignedStatus
from app.repositories import GameRepository

class MissionRepository:
    """Repository for the mission model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_mission(self, mission_id: UUID) -> Mission | None:
        """Get a mission by ID"""
        result = await self.db.execute(select(Mission).where(Mission.id == mission_id))
        return result.scalar_one_or_none()
    
    async def get_missions_by_game(self, game_id: UUID) -> list[Mission]:
        """Get all missions for a game"""
        result = await self.db.execute(
            select(Mission).where(Mission.game_id == game_id)
        )
        return list(result.scalars().all())
    
    # CRUD
    async def create_mission(self, mission_data: MissionCreate) -> Mission:
        """Create a new mission"""
        mission = Mission(**mission_data.model_dump())
        if mission_data.game_id is not None:
            # Vérifier que le game_id correspond à un game existant
            game_repo = GameRepository(self.db)
            game = await game_repo.get_game(mission_data.game_id)
            if game is None:
                raise HTTPException(status_code=404, detail="Game not found")
        self.db.add(mission)
        await self.db.commit()
        await self.db.refresh(mission)
        return mission
    

    async def update_mission(self, mission_id: UUID, mission_data: MissionUpdate) -> Mission:
        """Update a mission"""
        mission = await self.get_mission(mission_id)
        if mission:
            for field, value in mission_data.model_dump(exclude_unset=True).items():
                setattr(mission, field, value)
            await self.db.commit()
            await self.db.refresh(mission)
            return mission


    async def delete_mission(self, mission_id: UUID) -> bool:
        """Delete a mission"""
        mission = await self.get_mission(mission_id)
        if mission:
            await self.db.delete(mission)
            await self.db.commit()
            return True
        return False

    async def get_available_missions(
        self, 
        game_id: UUID, 
        player_id: UUID,
        exclude_assigned_to_player: bool = True
    ) -> list[Mission]:
        """Get missions available for a player (not yet assigned or not completed)"""
        query = select(Mission).where(Mission.game_id == game_id)
        
        if exclude_assigned_to_player:
            # Exclure les missions déjà assignées à ce joueur
            assigned_mission_ids = await self.db.execute(
                select(MissionAssigned.mission_id).where(MissionAssigned.player_id == player_id)
            )
            assigned_ids = [row[0] for row in assigned_mission_ids.fetchall()]
            if assigned_ids:
                query = query.where(~Mission.id.in_(assigned_ids))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def assign_mission_to_player(
        self, 
        player_id: UUID, 
        mission_id: UUID
    ) -> MissionAssigned:
        """Assign a mission to a player"""
        mission_assigned = MissionAssigned(
            player_id=player_id,
            mission_id=mission_id,
            status=MissionAssignedStatus.ACTIVE
        )
        self.db.add(mission_assigned)
        await self.db.commit()
        await self.db.refresh(mission_assigned)
        return mission_assigned
    
    async def get_assignments_by_players_and_date(
        self,
        player_ids: List[UUID],
        assigned_since: datetime
    ) -> List[MissionAssigned]:
        """
        Récupérer toutes les missions assignées pour des joueurs depuis une date donnée.
        
        Args:
            player_ids: Liste des IDs des joueurs
            assigned_since: Date minimale d'assignation (assigned_at >= assigned_since)
        
        Returns:
            Liste des missions assignées correspondant aux critères
        """
        result = await self.db.execute(
            select(MissionAssigned).where(
                and_(
                    MissionAssigned.player_id.in_(player_ids),
                    MissionAssigned.assigned_at >= assigned_since
                )
            )
        )
        return list(result.scalars().all())

