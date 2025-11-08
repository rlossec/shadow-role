
from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel
from uuid import UUID
from models.lobby import LobbyStatus

if TYPE_CHECKING:
    from schemas.game import GameResponse


class LobbyBase(BaseModel):
    name: str
    game_id: UUID
    max_players: int = 10


class LobbyCreate(LobbyBase):
    pass


class LobbyUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[LobbyStatus] = None
    max_players: Optional[int] = None


class LobbyResponse(LobbyBase):
    id: UUID
    code: str
    host_id: UUID
    status: LobbyStatus
    current_players: int
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class LobbyWithGame(LobbyResponse):
    game: "GameResponse"  # Forward reference - sera résolu par model_rebuild()

    class Config:
        from_attributes = True

