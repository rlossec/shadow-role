from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from models.mission import MissionType


class MissionBase(BaseModel):
    title: str
    description: str
    type: MissionType = MissionType.MISSION
    difficulty: int  # 0-100
    image_url: Optional[str] = None


class MissionCreate(MissionBase):
    game_id: UUID
    created_by: Optional[UUID] = None


class MissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[MissionType] = None
    difficulty: Optional[int] = None
    image_url: Optional[str] = None


class MissionResponse(MissionBase):
    id: UUID
    game_id: UUID
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True
