"""SQLAlchemy ORM model for authentication tokens."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.adapters.db.db_adapter import Base
from src.core.domain.entity import TokenType


class AuthTokenModel(Base):
    """
    ORM model for authentication tokens.
    
    Stores JWT tokens in the database for validation, revocation, and auditing.
    """
    
    __tablename__ = "auth_tokens"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User reference
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Token details
    token_type = Column(SQLEnum(TokenType, name="token_type"), nullable=False, index=True)
    token_string = Column(String(500), unique=True, nullable=False, index=True)
    
    # Expiration and lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index("idx_auth_tokens_user_type", "user_id", "token_type"),
        Index("idx_auth_tokens_user_revoked", "user_id", "revoked"),
        Index("idx_auth_tokens_expires", "expires_at", "revoked"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AuthTokenModel(id={self.id}, user_id={self.user_id}, "
            f"type={self.token_type}, revoked={self.revoked})>"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token_type": self.token_type.value if self.token_type else None,
            "token_string": self.token_string,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "revoked": self.revoked,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
