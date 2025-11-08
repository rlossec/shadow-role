from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from db.database import Base


class Mission(Base):
    __tablename__ = "missions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 0-100
    estimated_duration_minutes = Column(Integer, nullable=False)
    is_known_by_player = Column(Boolean, nullable=False, default=True)
    is_known_by_others = Column(Boolean, nullable=False, default=False)

    # Relations
    game = relationship("Game", back_populates="missions")
    role = relationship("Role", back_populates="missions")
    mission_players = relationship("MissionPlayer", back_populates="mission", cascade="all, delete-orphan")

