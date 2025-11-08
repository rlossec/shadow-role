from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid

from db.database import Base


class GameType(str, enum.Enum):
    ROLE_BASED = "role_based"
    MISSION_BASED = "mission_based"
    HYBRID = "hybrid"


class Game(Base):
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    rules = Column(Text, nullable=False)
    type = Column(SQLEnum(GameType), nullable=False)
    config = Column(JSON, nullable=True)  # Configuration dynamique
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    lobbies = relationship("Lobby", back_populates="game", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="game", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="game", cascade="all, delete-orphan")

