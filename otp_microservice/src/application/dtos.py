"""OTP Data Transfer Objects."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class GenerateOTPRequest(BaseModel):
    """Request to generate OTP."""
    
    user_id: str = Field(..., description="User ID for OTP generation")
    delivery_method: str = Field(
        default="email",
        description="Delivery method (email or sms)",
        pattern="^(email|sms)$"
    )
    recipient: Optional[str] = Field(None, description="Email address or phone number (optional)")
    
    @field_validator("delivery_method")
    @classmethod
    def validate_delivery_method(cls, v: str) -> str:
        """Validate delivery method."""
        if v not in ["email", "sms"]:
            raise ValueError("Delivery method must be 'email' or 'sms'")
        return v


class GenerateOTPResponse(BaseModel):
    """Response from OTP generation."""
    
    otp_id: str = Field(..., description="OTP identifier")
    expires_at: str = Field(..., description="Expiration timestamp (ISO 8601)")
    delivery_method: str = Field(..., description="How OTP was delivered")
    recipient: str = Field(..., description="Where OTP was sent (masked)")
    otp_code: Optional[str] = Field(None, description="OTP code (only in development mode)")


class ValidateOTPRequest(BaseModel):
    """Request to validate OTP."""
    
    otp_id: str = Field(..., description="OTP ID to validate")
    otp_code: str = Field(
        ...,
        description="OTP code to validate",
        min_length=6,
        max_length=6,
        pattern="^[0-9]{6}$"
    )
    
    @field_validator("otp_code")
    @classmethod
    def validate_otp_code(cls, v: str) -> str:
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError("OTP code must contain only digits")
        if len(v) != 6:
            raise ValueError("OTP code must be exactly 6 digits")
        return v


class ValidateOTPResponse(BaseModel):
    """Response from OTP validation."""
    
    valid: bool = Field(..., description="Whether OTP is valid")
    user_id: Optional[str] = Field(default=None, description="User ID if validation successful")
    email: Optional[str] = Field(default=None, description="User email if validation successful")
    message: str = Field(..., description="Validation result message")
    attempts_remaining: Optional[int] = Field(
        default=None,
        description="Remaining validation attempts"
    )


class OTPStatusResponse(BaseModel):
    """OTP status information."""
    
    otp_id: str
    user_id: str
    status: str
    delivery_method: str
    created_at: str
    expires_at: str
    attempts: int
    max_attempts: int


__all__ = [
    "GenerateOTPRequest",
    "GenerateOTPResponse",
    "ValidateOTPRequest",
    "ValidateOTPResponse",
    "OTPStatusResponse",
]
