"""Auth Domain Exceptions and Error Codes.

Centralized error handling for auth_microservice.
"""
from enum import Enum
from typing import Optional


class AuthErrorCode(str, Enum):
    """Standardized error codes for auth microservice."""
    
    # Authentication errors (AUTH_001-099)
    INVALID_CREDENTIALS = "AUTH_001"
    TOKEN_EXPIRED = "AUTH_002"
    INVALID_TOKEN = "AUTH_003"
    MISSING_AUTH_HEADER = "AUTH_004"
    INVALID_REFRESH_TOKEN = "AUTH_007"
    
    # Service integration errors (AUTH_100-199)
    USERS_SERVICE_UNAVAILABLE = "AUTH_101"
    OTP_SERVICE_UNAVAILABLE = "AUTH_102"
    
    # OTP errors (AUTH_200-299)
    OTP_VERIFICATION_REQUIRED = "AUTH_201"
    INVALID_OTP = "AUTH_202"
    OTP_EXPIRED = "AUTH_203"
    
    # General errors (AUTH_900-999)
    INTERNAL_ERROR = "AUTH_900"
    VALIDATION_ERROR = "AUTH_901"


class AuthException(Exception):
    """Base exception for auth domain."""
    
    def __init__(
        self,
        code: AuthErrorCode,
        message: str,
        details: Optional[str] = None,
        status_code: int = 500,
    ):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)


class InvalidCredentialsException(AuthException):
    """Raised when credentials are invalid."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.INVALID_CREDENTIALS,
            message="Invalid credentials",
            details=details or "Username or password is incorrect",
            status_code=401,
        )


class TokenExpiredException(AuthException):
    """Raised when JWT token has expired."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.TOKEN_EXPIRED,
            message="Token has expired",
            details=details or "The provided token has expired. Please login again.",
            status_code=401,
        )


class InvalidTokenException(AuthException):
    """Raised when JWT token is invalid."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.INVALID_TOKEN,
            message="Invalid token",
            details=details or "The provided token is invalid or malformed",
            status_code=401,
        )


class MissingAuthHeaderException(AuthException):
    """Raised when Authorization header is missing."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.MISSING_AUTH_HEADER,
            message="Missing authorization header",
            details=details or "Authorization header is required",
            status_code=401,
        )


class InvalidRefreshTokenException(AuthException):
    """Raised when refresh token is invalid."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.INVALID_REFRESH_TOKEN,
            message="Invalid refresh token",
            details=details or "The provided refresh token is invalid or expired",
            status_code=401,
        )


class UsersServiceUnavailableException(AuthException):
    """Raised when users_microservice is unavailable."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.USERS_SERVICE_UNAVAILABLE,
            message="Users service unavailable",
            details=details or "Unable to connect to users service",
            status_code=503,
        )


class OTPServiceUnavailableException(AuthException):
    """Raised when otp_microservice is unavailable."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.OTP_SERVICE_UNAVAILABLE,
            message="OTP service unavailable",
            details=details or "Unable to connect to OTP service",
            status_code=503,
        )


class OTPVerificationRequiredException(AuthException):
    """Raised when OTP verification is required."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.OTP_VERIFICATION_REQUIRED,
            message="OTP verification required",
            details=details or "Two-factor authentication is required",
            status_code=403,
        )


class InvalidOTPException(AuthException):
    """Raised when OTP is invalid or expired."""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code=AuthErrorCode.INVALID_OTP,
            message="Invalid OTP",
            details=details or "The provided OTP code is invalid or expired",
            status_code=401,
        )


__all__ = [
    "AuthErrorCode",
    "AuthException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "InvalidTokenException",
    "MissingAuthHeaderException",
    "InvalidRefreshTokenException",
    "UsersServiceUnavailableException",
    "OTPServiceUnavailableException",
    "OTPVerificationRequiredException",
    "InvalidOTPException",
]
