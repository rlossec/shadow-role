import secrets

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, noload

from app.models import Lobby, Game, Player, MissionAssigned
from app.schemas import LobbyCreate, LobbyUpdate


LOBBY_CODE_LENGTH = 8


class LobbyRepository:
    """Repository for the lobby model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _generate_code(self) -> str:
        """Generate a unique lobby code"""
        return secrets.token_urlsafe(6).upper()[:LOBBY_CODE_LENGTH]
    
    async def get_lobby(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby by ID"""
        result = await self.db.execute(select(Lobby).where(Lobby.id == lobby_id))
        return result.unique().scalar_one_or_none()
    
    async def get_lobby_with_game_and_missions(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby with game and game.missions loaded (for round start validation)"""
        result = await self.db.execute(
            select(Lobby)
            .options(
                selectinload(Lobby.game).selectinload(Game.missions)
            )
            .where(Lobby.id == lobby_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_lobby_with_rounds(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby with rounds loaded (for counting rounds)"""
        result = await self.db.execute(
            select(Lobby)
            .options(
                selectinload(Lobby.rounds)
            )
            .where(Lobby.id == lobby_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_lobby_with_game_missions_and_rounds(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby with game, missions and rounds loaded (for start_round)"""
        result = await self.db.execute(
            select(Lobby)
            .options(
                selectinload(Lobby.game).selectinload(Game.missions),
                selectinload(Lobby.rounds)
            )
            .where(Lobby.id == lobby_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_lobby_with_game_and_players(self, lobby_id: UUID) -> Lobby | None:
        """Get a lobby with game and players (including user and missions for each player)"""
        # Expirer tous les objets Lobby de la session pour forcer le rechargement
        from sqlalchemy.orm import Session
        if hasattr(self.db, 'expire_all'):
            self.db.expire_all()
        
        result = await self.db.execute(
            select(Lobby)
            .options(
                selectinload(Lobby.game).selectinload(Game.tags),
                selectinload(Lobby.players).selectinload(Player.user),
                selectinload(Lobby.players).selectinload(Player.mission_assigned).selectinload(MissionAssigned.mission)
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
                selectinload(Lobby.game).selectinload(Game.tags),
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

        payload = lobby_data.model_dump()

        lobby = Lobby(
            **payload,
            host_id=host_id,
            code=code,
        )
        self.db.add(lobby)
        await self.db.commit()
        await self.db.refresh(lobby)
        
        # Recharger le lobby avec le game (sans tags, non nécessaires pour les lobbies)
        # pour éviter le lazy loading lors de la validation Pydantic
        result = await self.db.execute(
            select(Lobby)
            .options(
                selectinload(Lobby.game).noload(Game.tags),  # Empêche le lazy loading des tags
            )
            .where(Lobby.id == lobby.id)
        )
        lobby = result.unique().scalar_one()
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

    async def delete_lobby(self, lobby_id: UUID) -> bool:
        """Delete a lobby"""
        lobby = await self.get_lobby(lobby_id)
        if lobby:
            await self.db.delete(lobby)
            await self.db.commit()
            return True
        return False

