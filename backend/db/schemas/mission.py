from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class MissionBase(BaseModel):
    title: str
    description: str
    difficulty: int  # 0-100
    estimated_duration_minutes: int
    is_known_by_player: bool
    is_known_by_others: bool


class MissionCreate(MissionBase):
    game_id: UUID
    role_id: Optional[UUID] = None


class MissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    estimated_duration_minutes: Optional[int] = None
    is_known_by_player: Optional[bool] = None
    is_known_by_others: Optional[bool] = None
    role_id: Optional[UUID] = None


class MissionResponse(MissionBase):
    id: UUID
    game_id: UUID
    role_id: Optional[UUID] = None

    class Config:
        from_attributes = True
