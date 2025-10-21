"""SQLAlchemy ORM Models for Users Microservice.

These models define the database schema.
"""
import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Index, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Define user_role enum matching the database enum
class UserRoleEnum(str, Enum):
    """User role enumeration."""
    ROOT = "root"
    EXTERNAL = "external"
    USER_SIATA = "user_siata"
    ADMIN = "admin"

# Define user_status enum matching the database enum
class UserStatusEnum(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_ACTIVATION = "pending_activation"


class UserModel(Base):
    """User table model."""
    
    __tablename__ = "users"
    
    # Primary Key - Maps to user_id column in DB
    id = Column("user_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User info - Maps to first_name and last_name columns in DB
    name = Column("first_name", String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Additional user fields
    phone_number = Column(String(20), nullable=True)
    
    # Role and team
    role = Column(SQLEnum('root', 'external', 'user_siata', 'admin', name='user_role', schema='siata_auth', native_enum=True), nullable=False, default="external", index=True)
    team_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Status fields
    status = Column(SQLEnum('active', 'inactive', 'suspended', 'pending_activation', name='user_status', schema='siata_auth', native_enum=True), nullable=False, default="pending_activation")
    is_mfa_enabled = Column(Boolean, nullable=False, default=False)
    
    # Login tracking
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    must_change_password = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    disabled_at = Column(DateTime(timezone=True), nullable=True)
    disabled_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Indexes and schema configuration
    __table_args__ = (
        Index('ix_users_username_active', 'username', 'status'),
        Index('ix_users_role_active', 'role', 'status'),
        {"schema": "siata_auth"},
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary (excluding password_hash)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "last_name": self.last_name,
            "role": self.role,
            "team_id": self.team_id,
            "status": self.status,
            "is_mfa_enabled": self.is_mfa_enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


__all__ = ["Base", "UserModel"]
