
from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from models.lobby import LobbyStatus, LobbyPhase

from .game import GameResponse
from .player import PlayerResponse
from .round import RoundResponse
from .mission import MissionResponse


class LobbyBase(BaseModel):
    name: str
    game_id: UUID
    min_players: int = 2
    max_players: int = 10


class LobbyCreate(LobbyBase):
    pass


class LobbyUpdate(BaseModel):
    name: Optional[str] = None
    game_id: Optional[UUID] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    host_id: Optional[UUID] = None
    status: Optional[LobbyStatus] = None
    phase: Optional[LobbyPhase] = None



class LobbyResponse(LobbyBase):
    id: UUID
    code: str
    host_id: UUID
    status: LobbyStatus
    phase: LobbyPhase
    created_at: datetime
    updated_at: datetime
    game: Optional["GameResponse"] = None
    players: Optional[List[PlayerResponse]] = None
    rounds: Optional[List[RoundResponse]] = None
    missions: Optional[List[MissionResponse]] = None

    class Config:
        from_attributes = True

