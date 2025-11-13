from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, String, Table, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import uuid

from db.database import Base


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
    game_type_id = Column(UUID(as_uuid=True), ForeignKey("game_types.id", ondelete="SET NULL"))

    # Relations
    game_type = relationship("GameType", back_populates="games")
    lobbies = relationship("Lobby", back_populates="game", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="game", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=GameTag, back_populates="games")



class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, index=True)

    # Relations
    games = relationship("Game", secondary=GameTag, back_populates="tags")


class GameType(Base):
    __tablename__ = "game_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)

    # Relations
    games = relationship("Game", back_populates="game_type", cascade="all, delete-orphan")
