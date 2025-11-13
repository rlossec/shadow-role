from uuid import UUID
from datetime import datetime

from typing import Optional, Any, List, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, field_validator

if TYPE_CHECKING:
    from .mission import MissionResponse


class GameBase(BaseModel):
    name: str
    description: str
    game_type_id: UUID
    image_url: Optional[str] = None
    min_players: int = 0
    max_players: int = 0
    tags: Optional[List[str]] = None


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    tags: Optional[List[str]] = None


class GameResponse(GameBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator('tags', mode='before')
    @classmethod
    def convert_tags_to_names(cls, v: Any) -> Optional[List[str]]:
        """
        Ce validateur s'exécute *avant* la validation standard.
        'v' sera la liste d'objets [Tag, Tag, ...] venant de l'ORM.
        """
        # Si 'v' est None, on retourne None
        if v is None:
            return None

        # Si 'v' est une liste (cas de la relation SQLAlchemy)
        if isinstance(v, list):
            # Gère le cas d'une liste vide
            if not v:
                return []
            
            # Tente de convertir la liste d'objets en liste de noms
            # On vérifie que le premier élément a bien 'name'
            # pour éviter les erreurs si la liste est déjà [str]
            if hasattr(v[0], 'name'):
                return [tag.name for tag in v]
        
        # Si 'v' est déjà une liste de strings ou autre,
        # on le laisse passer tel quel pour la validation Pydantic standard.
        return v


class GameResponseWithMissions(GameResponse):
    missions: List["MissionResponse"]
