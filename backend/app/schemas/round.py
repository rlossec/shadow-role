
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.round import RoundStatus


class RoundBase(BaseModel):
    lobby_id: UUID


class RoundCreate(RoundBase):
    round_number: int


class RoundResponse(RoundBase):
    id: UUID
    round_number: int
    status: RoundStatus
    started_at: datetime
    ended_at: datetime
