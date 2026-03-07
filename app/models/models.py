import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    token = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    last_active_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")
    turns = relationship("Turn", back_populates="session", cascade="all, delete-orphan")
    ratings = relationship("UserRating", back_populates="session", cascade="all, delete-orphan")


class Conversation(Base):
    """阶段1仅建表，不编写业务代码。未来用于多对话支持和长期记忆。"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    turn_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    session = relationship("Session", back_populates="conversations")


class Turn(Base):
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    turn_index = Column(Integer, nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    emotion_label = Column(String(50), nullable=True)
    is_crisis = Column(Boolean, nullable=False, default=False)
    bert_latency_ms = Column(Integer, nullable=True)
    llm_latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    session = relationship("Session", back_populates="turns")

    __table_args__ = (
        UniqueConstraint("session_id", "turn_index", name="uq_session_turn"),
    )


class CrisisRule(Base):
    __tablename__ = "crisis_rules"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(255), nullable=False)
    response_template = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False, default=0)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class UserRating(Base):
    __tablename__ = "user_ratings"

    id = Column(Integer, primary_key=True)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    rating_type = Column(Enum("before", "after", name="rating_type_enum"), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    session = relationship("Session", back_populates="ratings")

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 10", name="check_score_range"),
    )
