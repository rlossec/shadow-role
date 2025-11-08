from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class RoleBase(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None
    min_players: int = 0


class RoleCreate(RoleBase):
    game_id: UUID


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    min_players: Optional[int] = None


class RoleResponse(RoleBase):
    id: UUID
    game_id: UUID

    class Config:
        from_attributes = True

