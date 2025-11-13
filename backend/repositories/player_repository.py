from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from uuid import UUID

from schemas import MissionResponse
from models import Player, PlayerStatus, MissionAssigned
from schemas import PlayerCreate, PlayerUpdate


class PlayerRepository:
    """Repository for the player model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_player(self, player_id: UUID) -> Player | None:
        """Get a player by ID"""
        result = await self.db.execute(select(Player).where(Player.id == player_id))
        return result.scalar_one_or_none()
    
    async def get_player_with_relations(self, player_id: UUID) -> Player | None:
        """Get a player with user, missions and lobby"""
        result = await self.db.execute(
            select(Player)
            .options(
                selectinload(Player.user),
                selectinload(Player.mission_assigned),
                selectinload(Player.lobby)
            )
            .where(Player.id == player_id)
        )
        return result.scalar_one_or_none()
    
    async def get_players_by_lobby(self, lobby_id: UUID) -> list[Player]:
        """Get all players in a lobby"""
        result = await self.db.execute(
            select(Player)
            .options(selectinload(Player.user), selectinload(Player.mission_assigned))
            .where(Player.lobby_id == lobby_id)
        )
        return list(result.scalars().all())
    
    async def get_active_player_by_user(self, user_id: UUID) -> Player | None:
        """Get active player (waiting or playing) for a user"""
        result = await self.db.execute(
            select(Player).where(
                and_(
                    Player.user_id == user_id,
                    Player.status.in_([PlayerStatus.WAITING, PlayerStatus.PLAYING])
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_player(self, player_data: PlayerCreate, user_id: UUID) -> Player:
        """Create a new player"""
        player = Player(
            lobby_id=player_data.lobby_id,
            user_id=user_id,
            status=PlayerStatus.WAITING
        )
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player
    
    async def update_player(self, player_id: UUID, player_data: PlayerUpdate) -> Player:
        """Update a player"""
        player = await self.get_player(player_id)
        if not player:
            raise ValueError("Player not found")
        if player_data.score is not None:
            player.score = player_data.score
        if player_data.status is not None:
            player.status = player_data.status
        await self.db.commit()
        await self.db.refresh(player)
        return player
    
    async def delete_player(self, player_id: UUID) -> bool:
        """Delete a player"""
        player = await self.get_player(player_id)
        if player:
            await self.db.delete(player)
            await self.db.commit()
            return True
        return False

    async def get_player_missions(self, player_id: UUID, skip: int = 0, limit: int = 100) -> List[MissionResponse]:
        """Get the missions for a player"""
        result = await self.db.execute(
            select(MissionAssigned)
            .where(MissionAssigned.player_id == player_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
