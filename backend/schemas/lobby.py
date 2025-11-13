
from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel

from models.lobby import LobbyStatus, LobbyPhase

if TYPE_CHECKING:
    from schemas.game import GameResponse
else:
    GameResponse = "GameResponse"


class LobbyBase(BaseModel):
    name: str
    game_id: UUID
    max_players: int = 10


class LobbyCreate(LobbyBase):
    pass


class LobbyUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[LobbyStatus] = None
    phase: Optional[LobbyPhase] = None
    max_players: Optional[int] = None


class LobbyResponse(LobbyBase):
    id: UUID
    code: str
    host_id: UUID
    status: LobbyStatus
    phase: LobbyPhase
    current_players: int
    created_at: datetime
    expires_at: datetime
    game: Optional["GameResponse"] = None

    class Config:
        from_attributes = True

