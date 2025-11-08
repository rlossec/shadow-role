from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from models import Mission, MissionPlayer, MissionPlayerStatus


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
    
    async def get_missions_by_role(self, role_id: UUID) -> list[Mission]:
        """Get all missions for a role"""
        result = await self.db.execute(
            select(Mission).where(Mission.role_id == role_id)
        )
        return list(result.scalars().all())
    
    async def get_available_missions(
        self, 
        game_id: UUID, 
        player_id: UUID,
        exclude_completed: bool = True
    ) -> list[Mission]:
        """Get missions available for a player (not yet assigned or not completed)"""
        # Missions non liées à un rôle spécifique ou missions liées mais pas encore assignées
        query = select(Mission).where(Mission.game_id == game_id)
        
        if exclude_completed:
            # Exclure les missions déjà complétées par ce joueur
            completed_mission_ids = await self.db.execute(
                select(MissionPlayer.mission_id).where(
                    and_(
                        MissionPlayer.player_id == player_id,
                        MissionPlayer.status.in_([MissionPlayerStatus.COMPLETED, MissionPlayerStatus.FAILED])
                    )
                )
            )
            completed_ids = [row[0] for row in completed_mission_ids.fetchall()]
            if completed_ids:
                query = query.where(~Mission.id.in_(completed_ids))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def assign_mission_to_player(
        self, 
        player_id: UUID, 
        mission_id: UUID,
        state: dict | None = None
    ) -> MissionPlayer:
        """Assign a mission to a player"""
        
        
        mission_player = MissionPlayer(
            player_id=player_id,
            mission_id=mission_id,
            status=MissionPlayerStatus.ACTIVE,
            state=state
        )
        self.db.add(mission_player)
        await self.db.commit()
        await self.db.refresh(mission_player)
        return mission_player

