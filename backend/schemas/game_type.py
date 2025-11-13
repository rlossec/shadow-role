from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class GameTypeBase(BaseModel):
    name: str
    description: str

class GameTypeCreate(GameTypeBase):
    pass

class GameTypeUpdate(GameTypeBase):
    pass

class GameTypeResponse(GameTypeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime