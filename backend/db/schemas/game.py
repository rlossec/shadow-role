from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID
from models.game import GameType


class GameBase(BaseModel):
    name: str
    description: str
    rules: str
    type: GameType
    config: Optional[Dict[str, Any]] = None


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[str] = None
    type: Optional[GameType] = None
    config: Optional[Dict[str, Any]] = None


class GameResponse(GameBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

