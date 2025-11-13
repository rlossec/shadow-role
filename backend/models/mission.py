
from datetime import datetime, timezone

import uuid
import enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


from db.database import Base


class MissionType(str, enum.Enum):
    MISSION = "mission"
    ROLE = "role"
    HYBRID = "hybrid"


class Mission(Base):
    __tablename__ = "missions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    type = Column(SQLEnum(MissionType), nullable=False, default=MissionType.MISSION)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    difficulty = Column(Integer, nullable=False)  # 0-100
    mission_assigned = relationship("MissionAssigned", back_populates="mission", cascade="all, delete-orphan")

    # Relations
    game = relationship("Game", back_populates="missions")
    players = relationship("MissionAssigned", back_populates="mission", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


