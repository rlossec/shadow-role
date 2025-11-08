import secrets
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from models import Lobby, LobbyStatus, Player, PlayerStatus
from db.schemas import LobbyCreate, LobbyUpdate


class LobbyRepository:
    """Repository for the lobby model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _generate_code(self) -> str:
        """Generate a unique lobby code"""
        return secrets.token_urlsafe(6).upper()[:8]  # 8 caractères
    
    async def get_lobby(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby by ID"""
        result = await self.db.execute(select(Lobby).where(Lobby.id == lobby_id))
        return result.scalar_one_or_none()
    
    async def get_lobby_with_relations(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby with game and players"""
        result = await self.db.execute(
            select(Lobby)
            .options(selectinload(Lobby.game), selectinload(Lobby.players))
            .where(Lobby.id == lobby_id)
        )
        return result.scalar_one_or_none()
    
    async def get_lobby_by_code(self, code: str) -> Lobby | None:
        """Get a lobby by code"""
        result = await self.db.execute(select(Lobby).where(Lobby.code == code))
        return result.scalar_one_or_none()
    
    async def get_public_lobbies(self, skip: int = 0, limit: int = 100) -> list[Lobby]:
        """Get public lobbies (waiting status)"""
        result = await self.db.execute(
            select(Lobby)
            .where(Lobby.status == LobbyStatus.WAITING)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create_lobby(self, lobby_data: LobbyCreate, host_id: UUID) -> Lobby:
        """Create a new lobby"""
        # Générer un code unique
        code = self._generate_code()
        while await self.get_lobby_by_code(code):
            code = self._generate_code()
        
        lobby = Lobby(
            **lobby_data.model_dump(),
            host_id=host_id,
            code=code,
            current_players=0
        )
        self.db.add(lobby)
        await self.db.commit()
        await self.db.refresh(lobby)
        return lobby
    
    async def update_lobby(self, lobby_id: UUID, lobby_data) -> Lobby:
        """Update a lobby"""
        lobby = await self.get_lobby(lobby_id)
        if not lobby:
            raise ValueError("Lobby not found")
        
        if lobby_data.status is not None:
            lobby.status = lobby_data.status
        if lobby_data.name is not None:
            lobby.name = lobby_data.name
        if lobby_data.max_players is not None:
            lobby.max_players = lobby_data.max_players
        
        await self.db.commit()
        await self.db.refresh(lobby)
        return lobby
    
    async def update_current_players(self, lobby_id: UUID) -> None:
        """Update current_players count for a lobby"""
        from models.player import Player, PlayerStatus
        result = await self.db.execute(
            select(func.count(Player.id)).where(
                and_(
                    Player.lobby_id == lobby_id,
                    Player.status.in_([PlayerStatus.WAITING, PlayerStatus.PLAYING])
                )
            )
        )
        count = result.scalar() or 0
        
        lobby = await self.get_lobby(lobby_id)
        if lobby:
            lobby.current_players = count
            await self.db.commit()
    
    async def delete_lobby(self, lobby_id: UUID) -> bool:
        """Delete a lobby"""
        lobby = await self.get_lobby(lobby_id)
        if lobby:
            await self.db.delete(lobby)
            await self.db.commit()
            return True
        return False

