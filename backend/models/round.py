import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base


class RoundStatus(str, enum.Enum):
    RUNNING = "running"
    FINISHED = "finished"


class Round(Base):
    __tablename__ = "rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    lobby_id = Column(UUID(as_uuid=True), ForeignKey("lobbies.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    status = Column(SQLEnum(RoundStatus), nullable=False, default=RoundStatus.RUNNING, index=True)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    lobby = relationship("Lobby", back_populates="rounds")