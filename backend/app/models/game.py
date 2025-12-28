
import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, String, Table, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship


from app.db.database import Base


class GameTypeEnum(str, enum.Enum):
    MISSION = "mission"
    ROLE = "role"
    HYBRID = "hybrid"

GameTag = Table(
    "game_tags",
    Base.metadata,
    Column("game_id", UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Game(Base):
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    min_players = Column(Integer, nullable=False, default=2)
    max_players = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    game_type = Column(SQLEnum(GameTypeEnum), nullable=False, default=GameTypeEnum.MISSION)


    lobbies = relationship("Lobby", back_populates="game", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="game", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=GameTag, back_populates="games")



class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, index=True)

    # Relations
    games = relationship("Game", secondary=GameTag, back_populates="tags")
