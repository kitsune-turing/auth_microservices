"""OTP Entity.

Core domain entity representing a One-Time Password.
"""
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class DeliveryMethod(str, Enum):
    """OTP delivery methods."""
    EMAIL = "email"
    SMS = "sms"


class OTPStatus(str, Enum):
    """OTP status."""
    PENDING = "pending"
    SENT = "sent"
    VALIDATED = "validated"
    EXPIRED = "expired"
    FAILED = "failed"


class OTP:
    """One-Time Password entity."""
    
    def __init__(
        self,
        user_id: str,
        code: str,
        delivery_method: DeliveryMethod,
        recipient: str,
        expires_in_minutes: int = 5,
        max_attempts: int = 3,
        otp_id: Optional[UUID] = None,
        status: OTPStatus = OTPStatus.PENDING,
        created_at: Optional[datetime] = None,
        attempts: int = 0,
    ):
        """
        Initialize OTP entity.
        
        Args:
            user_id: User ID for whom OTP is generated
            code: OTP code (6 digits typically)
            delivery_method: How to deliver the OTP
            recipient: Email address or phone number
            expires_in_minutes: OTP expiration time
            max_attempts: Maximum validation attempts
            otp_id: Unique OTP identifier
            status: Current OTP status
            created_at: Creation timestamp
            attempts: Number of validation attempts
        """
        self.otp_id = otp_id or uuid4()
        self.user_id = user_id
        self.code = code
        self.delivery_method = delivery_method
        self.recipient = recipient
        self.expires_in_minutes = expires_in_minutes
        self.max_attempts = max_attempts
        self.status = status
        self.created_at = created_at or datetime.now(UTC)
        self.expires_at = self.created_at + timedelta(minutes=expires_in_minutes)
        self.attempts = attempts
        self.validated_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if OTP has expired."""
        return datetime.now(UTC) > self.expires_at
    
    def is_valid_code(self, provided_code: str) -> bool:
        """
        Validate provided code against stored code.
        
        Args:
            provided_code: Code to validate
            
        Returns:
            True if codes match, False otherwise
        """
        return self.code == provided_code
    
    def can_attempt_validation(self) -> bool:
        """Check if more validation attempts are allowed."""
        return self.attempts < self.max_attempts
    
    def increment_attempts(self) -> None:
        """Increment validation attempts counter."""
        self.attempts += 1
    
    def mark_as_sent(self) -> None:
        """Mark OTP as successfully sent."""
        self.status = OTPStatus.SENT
    
    def mark_as_validated(self) -> None:
        """Mark OTP as successfully validated."""
        self.status = OTPStatus.VALIDATED
        self.validated_at = datetime.now(UTC)
    
    def mark_as_expired(self) -> None:
        """Mark OTP as expired."""
        self.status = OTPStatus.EXPIRED
    
    def mark_as_failed(self) -> None:
        """Mark OTP delivery as failed."""
        self.status = OTPStatus.FAILED
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary."""
        return {
            "otp_id": str(self.otp_id),
            "user_id": self.user_id,
            "delivery_method": self.delivery_method.value,
            "recipient": self.recipient,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
        }


__all__ = ["OTP", "DeliveryMethod", "OTPStatus"]
