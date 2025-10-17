"""OTP Domain Exceptions.

Custom exceptions for the OTP microservice with standardized error codes.
"""
from enum import Enum
from typing import Optional, Any


class OTPErrorCode(str, Enum):
    """OTP error codes (OTP_001-999)."""
    
    # Generation errors (001-099)
    OTP_GENERATION_FAILED = "OTP_001"
    INVALID_USER_ID = "OTP_002"
    INVALID_DELIVERY_METHOD = "OTP_003"
    DELIVERY_FAILED = "OTP_004"
    
    # Validation errors (100-199)
    OTP_VALIDATION_FAILED = "OTP_100"
    OTP_EXPIRED = "OTP_101"
    OTP_NOT_FOUND = "OTP_102"
    INVALID_OTP_CODE = "OTP_103"
    MAX_ATTEMPTS_EXCEEDED = "OTP_104"
    OTP_ALREADY_USED = "OTP_105"
    
    # User errors (200-299)
    USER_NOT_FOUND = "OTP_200"
    USER_INACTIVE = "OTP_201"
    NO_CONTACT_METHOD = "OTP_202"
    INVALID_EMAIL = "OTP_203"
    INVALID_PHONE = "OTP_204"
    
    # Service errors (300-399)
    EMAIL_SERVICE_ERROR = "OTP_300"
    SMS_SERVICE_ERROR = "OTP_301"
    NOTIFICATION_SERVICE_ERROR = "OTP_302"
    
    # Database errors (500-599)
    DATABASE_ERROR = "OTP_500"
    TRANSACTION_FAILED = "OTP_501"
    
    # General errors (900-999)
    INTERNAL_ERROR = "OTP_900"
    VALIDATION_ERROR = "OTP_901"
    UNKNOWN_ERROR = "OTP_999"


class OTPException(Exception):
    """Base exception for OTP domain."""
    
    def __init__(
        self,
        code: OTPErrorCode,
        message: str,
        details: Optional[dict[str, Any]] = None,
        status_code: int = 400,
    ):
        """
        Initialize OTP exception.
        
        Args:
            code: Error code from OTPErrorCode enum
            message: Human-readable error message
            details: Optional additional error details
            status_code: HTTP status code
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class OTPGenerationFailedException(OTPException):
    """Raised when OTP generation fails."""
    
    def __init__(self, user_id: str, reason: Optional[str] = None):
        details = {"user_id": user_id}
        if reason:
            details["reason"] = reason
            
        super().__init__(
            code=OTPErrorCode.OTP_GENERATION_FAILED,
            message="Failed to generate OTP",
            details=details,
            status_code=500,
        )


class OTPExpiredException(OTPException):
    """Raised when OTP has expired."""
    
    def __init__(self, otp_id: str):
        super().__init__(
            code=OTPErrorCode.OTP_EXPIRED,
            message="OTP has expired",
            details={"otp_id": otp_id},
            status_code=400,
        )


class OTPNotFoundException(OTPException):
    """Raised when OTP is not found."""
    
    def __init__(self, user_id: str):
        super().__init__(
            code=OTPErrorCode.OTP_NOT_FOUND,
            message="No active OTP found for user",
            details={"user_id": user_id},
            status_code=404,
        )


class InvalidOTPCodeException(OTPException):
    """Raised when OTP code is invalid."""
    
    def __init__(self, attempts_remaining: int):
        super().__init__(
            code=OTPErrorCode.INVALID_OTP_CODE,
            message="Invalid OTP code",
            details={"attempts_remaining": attempts_remaining},
            status_code=400,
        )


class MaxAttemptsExceededException(OTPException):
    """Raised when maximum OTP validation attempts exceeded."""
    
    def __init__(self, user_id: str):
        super().__init__(
            code=OTPErrorCode.MAX_ATTEMPTS_EXCEEDED,
            message="Maximum validation attempts exceeded",
            details={"user_id": user_id},
            status_code=429,
        )


class OTPAlreadyUsedException(OTPException):
    """Raised when trying to use an already validated OTP."""
    
    def __init__(self, otp_id: str):
        super().__init__(
            code=OTPErrorCode.OTP_ALREADY_USED,
            message="OTP has already been used",
            details={"otp_id": otp_id},
            status_code=400,
        )


class InvalidDeliveryMethodException(OTPException):
    """Raised when delivery method is invalid."""
    
    def __init__(self, method: str):
        super().__init__(
            code=OTPErrorCode.INVALID_DELIVERY_METHOD,
            message=f"Invalid delivery method: {method}",
            details={
                "provided_method": method,
                "allowed_methods": ["email", "sms"],
            },
            status_code=400,
        )


class DeliveryFailedException(OTPException):
    """Raised when OTP delivery fails."""
    
    def __init__(self, method: str, recipient: str, error: str):
        super().__init__(
            code=OTPErrorCode.DELIVERY_FAILED,
            message=f"Failed to deliver OTP via {method}",
            details={
                "method": method,
                "recipient": recipient,
                "error": error,
            },
            status_code=500,
        )


class NoContactMethodException(OTPException):
    """Raised when user has no valid contact method."""
    
    def __init__(self, user_id: str):
        super().__init__(
            code=OTPErrorCode.NO_CONTACT_METHOD,
            message="User has no valid contact method for OTP delivery",
            details={"user_id": user_id},
            status_code=400,
        )


class EmailServiceException(OTPException):
    """Raised when email service fails."""
    
    def __init__(self, error: str):
        super().__init__(
            code=OTPErrorCode.EMAIL_SERVICE_ERROR,
            message="Email service error",
            details={"error": error},
            status_code=503,
        )


class SMSServiceException(OTPException):
    """Raised when SMS service fails."""
    
    def __init__(self, error: str):
        super().__init__(
            code=OTPErrorCode.SMS_SERVICE_ERROR,
            message="SMS service error",
            details={"error": error},
            status_code=503,
        )


__all__ = [
    "OTPErrorCode",
    "OTPException",
    "OTPGenerationFailedException",
    "OTPExpiredException",
    "OTPNotFoundException",
    "InvalidOTPCodeException",
    "MaxAttemptsExceededException",
    "OTPAlreadyUsedException",
    "InvalidDeliveryMethodException",
    "DeliveryFailedException",
    "NoContactMethodException",
    "EmailServiceException",
    "SMSServiceException",
]
