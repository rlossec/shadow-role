import secrets

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, noload

from models import Lobby
from schemas import LobbyCreate, LobbyUpdate
from models.player import Player, PlayerStatus


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
        return result.unique().scalar_one_or_none()
    
    async def get_lobby_with_game_and_players(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby with game and players"""
        result = await self.db.execute(
            select(Lobby)
            .options(
                selectinload(Lobby.game),
                selectinload(Lobby.players)
            )
            .where(Lobby.id == lobby_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_lobby_by_code(self, code: str) -> Lobby | None:
        """Get a lobby by code"""
        result = await self.db.execute(select(Lobby).where(Lobby.code == code))
        return result.unique().scalar_one_or_none()

    async def get_lobby_with_game_and_players_by_code(self, code: str) -> Lobby | None:
        """Get a lobby by code including related game and players."""
        result = await self.db.execute(
            select(Lobby)
            .options(
                selectinload(Lobby.game),
                selectinload(Lobby.players)
            )
            .where(Lobby.code == code)
        )
        lobby = result.unique().scalar_one_or_none()
        return lobby
    
    async def get_lobbies(self, skip: int = 0, limit: int = 100) -> list[Lobby]:
        """Get lobbies"""
        result = await self.db.execute(
            select(Lobby)
            .options(
                noload(Lobby.game),     # Explicitly not load the game
                noload(Lobby.players),  # Don't load players for list
                noload(Lobby.rounds)    # Don't load rounds for list
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())
    
    async def create_lobby(self, lobby_data: LobbyCreate, host_id: UUID) -> Lobby:
        """Create a new lobby"""
        # Generate a unique code
        code = self._generate_code()
        while await self.get_lobby_by_code(code):
            code = self._generate_code()
        
        lobby = Lobby(
            **lobby_data.model_dump(),
            host_id=host_id,
            code=code,
        )
        self.db.add(lobby)
        await self.db.commit()
        await self.db.refresh(lobby)
        return lobby
    
    async def update_lobby(self, lobby_id: UUID, lobby_data: LobbyUpdate) -> Lobby:
        """Update a lobby"""
        lobby = await self.get_lobby(lobby_id)
        if not lobby:
            raise ValueError("Lobby not found")
        
        for field, value in lobby_data.model_dump(exclude_unset=True).items():
            setattr(lobby, field, value)
        
        await self.db.commit()
        await self.db.refresh(lobby)
        
        # Recharger avec les relations si nécessaire
        result = await self.db.execute(
            select(Lobby)
            .options(selectinload(Lobby.game), selectinload(Lobby.players))
            .where(Lobby.id == lobby_id)
        )
        updated_lobby = result.unique().scalar_one()
        return updated_lobby

    async def add_player(self, lobby_id: UUID, user_id: UUID) -> None:
        """Add a player to a lobby"""
        player = Player(lobby_id=lobby_id, user_id=user_id, status=PlayerStatus.WAITING)
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player
    
    async def update_current_players(self, lobby_id: UUID) -> None:
        """Update current_players count for a lobby"""
        
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

