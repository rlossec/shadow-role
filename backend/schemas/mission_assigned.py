from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from models.mission_assigned import MissionAssignedStatus


class MissionAssignedBase(BaseModel):
    player_id: UUID
    mission_id: UUID
    status: MissionAssignedStatus = MissionAssignedStatus.ACTIVE


class MissionAssignedCreate(MissionAssignedBase):
    pass


class MissionAssignedUpdate(BaseModel):
    status: Optional[MissionAssignedStatus] = None
    completed_at: Optional[datetime] = None


class MissionAssignedResponse(MissionAssignedBase):
    id: UUID
    assigned_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

