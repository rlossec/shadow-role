from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from app.models.player import PlayerStatus


class PlayerBase(BaseModel):
    lobby_id: UUID
    user_id: UUID
    alias: Optional[str] = None
    color: Optional[str] = None
    score: int = 0
    status: PlayerStatus = PlayerStatus.WAITING


class PlayerCreate(BaseModel):
    lobby_id: UUID
    alias: Optional[str] = None
    color: Optional[str] = None
    user_id: Optional[UUID] = None


class PlayerUpdate(BaseModel):
    user_id: Optional[UUID] = None
    alias: Optional[str] = None
    color: Optional[str] = None
    score: Optional[int] = None
    status: Optional[PlayerStatus] = None


class PlayerResponse(PlayerBase):
    id: UUID
    user_id: UUID
    alias: Optional[str] = None
    color: Optional[str] = None
    joined_at: datetime
    left_at: Optional[datetime] = None

    class Config:
        from_attributes = True
