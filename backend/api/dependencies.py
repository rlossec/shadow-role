
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_session

from repositories import GameRepository, MissionRepository, PlayerRepository, LobbyRepository

from services.auth import (
    get_authentication_service,
    get_current_user,
    get_current_active_user,
)

def get_lobby_repository(db: AsyncSession = Depends(get_async_session)):
    return LobbyRepository(db)

def get_game_repository(db: AsyncSession = Depends(get_async_session)):
    return GameRepository(db)

def get_mission_repository(db: AsyncSession = Depends(get_async_session)):
    return MissionRepository(db)

def get_player_repository(db: AsyncSession = Depends(get_async_session)):
    return PlayerRepository(db)


__all__ = [
    "get_authentication_service",
    "get_current_user",
    "get_current_active_user",
    "get_game_repository",
    "get_mission_repository",
    "get_player_repository",
]
