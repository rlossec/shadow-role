from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from models.player import PlayerStatus


class PlayerBase(BaseModel):
    lobby_id: UUID
    role_id: Optional[UUID] = None
    score: int = 0
    status: PlayerStatus = PlayerStatus.WAITING


class PlayerCreate(BaseModel):
    lobby_id: UUID


class PlayerUpdate(BaseModel):
    role_id: Optional[UUID] = None
    score: Optional[int] = None
    status: Optional[PlayerStatus] = None


class PlayerResponse(PlayerBase):
    id: UUID
    user_id: UUID
    joined_at: datetime
    left_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlayerWithUser(PlayerResponse):
    user: "UserResponse"  # Forward reference

    class Config:
        from_attributes = True


class PlayerWithRole(PlayerResponse):
    role: Optional["RoleResponse"] = None  # Forward reference

    class Config:
        from_attributes = True

