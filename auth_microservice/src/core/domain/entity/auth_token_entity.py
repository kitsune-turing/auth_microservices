"""SQLAlchemy ORM models for auth_microservice."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from ..adapters.db.db_adapter import Base
from src.core.domain.entity import TokenType


class AuthTokenModel(Base):
    """ORM model for authentication tokens."""
    
    __tablename__ = "auth_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_type = Column(SQLEnum(TokenType), nullable=False)
    token_string = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    revoked = Column(Boolean, default=False, nullable=False, index=True)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AuthTokenModel(id={self.id}, user_id={self.user_id}, "
            f"type={self.token_type})>"
        )


class SessionModel(Base):
    """ORM model for user sessions."""
    
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    access_token_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # Supports both IPv4 and IPv6
    user_agent = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_activity = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Composite index for efficient queries
    __table_args__ = (
        Index("idx_sessions_user_active", "user_id", "active"),
        Index("idx_sessions_user_expires", "user_id", "expires_at"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<SessionModel(id={self.id}, user_id={self.user_id}, "
            f"active={self.active})>"
        )