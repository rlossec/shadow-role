from uuid import UUID
from datetime import datetime

from typing import Optional, Any, List, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.game import GameTypeEnum

if TYPE_CHECKING:
    from .mission import MissionResponse


class GameBase(BaseModel):
    name: str
    game_type: Optional[GameTypeEnum] = GameTypeEnum.MISSION
    description: Optional[str] = None
    image_url: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    tags: Optional[List[str]] = None


class GameCreate(GameBase):
    game_type: GameTypeEnum = GameTypeEnum.MISSION


class GameUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    game_type: Optional[GameTypeEnum] = None
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
        Gère aussi le cas où tags n'est pas chargé (lazy loading).
        """
        # Si 'v' est None, on retourne None
        if v is None:
            return None

        # Vérifier si c'est une relation SQLAlchemy non chargée
        # en utilisant inspect pour éviter le lazy loading
        try:
            from sqlalchemy import inspect as sqlalchemy_inspect
            from sqlalchemy.orm import InstrumentedAttribute
            
            # Si v est un InstrumentedAttribute (relation non chargée),
            # on retourne None pour éviter le lazy loading
            if isinstance(v, InstrumentedAttribute):
                return None
            
            # Si v est un objet avec un état SQLAlchemy, vérifier si l'attribut est chargé
            # (ce cas ne devrait pas se produire car le validateur reçoit la valeur, pas l'objet)
        except (ImportError, AttributeError):
            pass

        # Si 'v' est une liste (cas de la relation SQLAlchemy chargée)
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
