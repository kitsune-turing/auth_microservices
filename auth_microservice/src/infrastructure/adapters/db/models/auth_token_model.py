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
    __table_args__ = {"schema": "siata_auth"}
    
    # Primary key - maps to token_id in database
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User reference
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Session reference - maps to session_id in database
    session_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Token details - token_type maps directly
    token_type = Column(SQLEnum(TokenType, name="token_type", schema="siata_auth"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Expiration and lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(UUID(as_uuid=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Composite indexes for efficient queries and schema configuration
    __table_args__ = (
        Index("idx_auth_tokens_user_type", "user_id", "token_type"),
        Index("idx_auth_tokens_user_revoked", "user_id", "is_revoked"),
        Index("idx_auth_tokens_expires", "expires_at", "is_revoked"),
        {"schema": "siata_auth"},
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AuthTokenModel(id={self.id}, user_id={self.user_id}, "
            f"type={self.token_type}, jti={self.jti}, revoked={self.revoked})>"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token_type": self.token_type.value if self.token_type else None,
            "token_hash": self.token_hash,
            "jti": str(self.jti),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "revoked": self.revoked,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
