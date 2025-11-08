from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid

from db.database import Base


class PlayerStatus(str, enum.Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    COMPLETED = "completed"
    LEFT = "left"


class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    lobby_id = Column(UUID(as_uuid=True), ForeignKey("lobbies.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    score = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(PlayerStatus), nullable=False, default=PlayerStatus.WAITING, index=True)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    lobby = relationship("Lobby", back_populates="players")
    user = relationship("User")
    role = relationship("Role", back_populates="players")
    mission_players = relationship("MissionPlayer", back_populates="player", cascade="all, delete-orphan")

    # Contraintes
    __table_args__ = (
        UniqueConstraint('lobby_id', 'user_id', name='uq_player_lobby_user'),
    )

