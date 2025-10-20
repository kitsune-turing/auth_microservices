"""SQLAlchemy OTP Model."""
from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DeliveryMethodEnum(str, PyEnum):
    """Delivery method enum for database."""
    EMAIL = "email"
    SMS = "sms"


class OTPStatusEnum(str, PyEnum):
    """OTP status enum for database."""
    PENDING = "pending"
    SENT = "sent"
    VALIDATED = "validated"
    EXPIRED = "expired"
    FAILED = "failed"


class OTPModel(Base):
    """SQLAlchemy model for OTP codes table."""
    
    __tablename__ = "otp_codes"
    __table_args__ = {"schema": "siata_auth"}
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    delivery_method = Column(
        Enum(DeliveryMethodEnum, name="delivery_method", schema="siata_auth"),
        nullable=False,
    )
    recipient = Column(String(255), nullable=False)
    status = Column(
        Enum(OTPStatusEnum, name="otp_status", schema="siata_auth"),
        nullable=False,
        default=OTPStatusEnum.PENDING,
    )
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<OTP(id={self.id}, user_id={self.user_id}, status={self.status})>"


__all__ = ["OTPModel", "DeliveryMethodEnum", "OTPStatusEnum", "Base"]
