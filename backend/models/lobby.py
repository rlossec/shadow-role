from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid

from db.database import Base


class LobbyStatus(str, enum.Enum):
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    ENDED = "ended"


class LobbyPhase(str, enum.Enum):
    NONE = "none"
    SUGGESTION = "suggestion"
    ROUND = "round"
    VALIDATION = "validation"


class Lobby(Base):
    __tablename__ = "lobbies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)  # Code d'invitation
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False)
    host_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(LobbyStatus), nullable=False, default=LobbyStatus.WAITING, index=True)
    phase = Column(SQLEnum(LobbyPhase), nullable=False, default=LobbyPhase.NONE, index=True)
    min_players = Column(Integer, nullable=False, default=2)
    max_players = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    game = relationship("Game", back_populates="lobbies", lazy="joined")
    host = relationship("User", foreign_keys=[host_id], lazy="joined")
    players = relationship("Player", back_populates="lobby", cascade="all, delete-orphan", lazy="joined")
    rounds = relationship("Round", back_populates="lobby", cascade="all, delete-orphan", lazy="joined")

