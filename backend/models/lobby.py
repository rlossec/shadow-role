from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid

from db.database import Base


class LobbyStatus(str, enum.Enum):
    WAITING = "waiting"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Lobby(Base):
    __tablename__ = "lobbies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)  # Code d'invitation
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False)
    host_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(LobbyStatus), nullable=False, default=LobbyStatus.WAITING, index=True)
    max_players = Column(Integer, nullable=False, default=10)
    current_players = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(hours=2))

    # Relations
    game = relationship("Game", back_populates="lobbies")
    host = relationship("User", foreign_keys=[host_id])
    players = relationship("Player", back_populates="lobby", cascade="all, delete-orphan")

