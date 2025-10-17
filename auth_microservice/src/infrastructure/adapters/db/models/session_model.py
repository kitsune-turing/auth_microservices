"""SQLAlchemy ORM model for user sessions."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Index,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.adapters.db.db_adapter import Base


class SessionModel(Base):
    """
    ORM model for user sessions.
    
    Tracks active user sessions with associated access tokens, IP addresses, and user agents.
    """
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User reference
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Associated access token
    access_token_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID of the access token associated with this session"
    )
    
    # Client information
    ip_address = Column(String(45), nullable=False, comment="Supports both IPv4 and IPv6")
    user_agent = Column(Text, nullable=False)
    
    # Session lifecycle
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_activity = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Session status
    active = Column(Boolean, default=True, nullable=False, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index("idx_sessions_user_active", "user_id", "active"),
        Index("idx_sessions_user_expires", "user_id", "expires_at"),
        Index("idx_sessions_access_token", "access_token_id"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<SessionModel(id={self.id}, user_id={self.user_id}, "
            f"active={self.active}, ip={self.ip_address})>"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "access_token_id": self.access_token_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "active": self.active,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }
