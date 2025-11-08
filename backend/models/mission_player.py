from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, DateTime, Enum as SQLEnum, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid

from db.database import Base


class MissionPlayerStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionPlayer(Base):
    __tablename__ = "mission_players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False, index=True)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False, index=True)
    state = Column(JSON, nullable=True)  # État évolutif de la mission
    status = Column(SQLEnum(MissionPlayerStatus), nullable=False, default=MissionPlayerStatus.ACTIVE, index=True)
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    player = relationship("Player", back_populates="mission_players")
    mission = relationship("Mission", back_populates="mission_players")

    # Contraintes
    __table_args__ = (
        UniqueConstraint('player_id', 'mission_id', name='uq_mission_player_player_mission'),
    )

