"""Domain exceptions."""
from .auth_exceptions import (
    AuthErrorCode,
    AuthException,
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException,
    MissingAuthHeaderException,
    InvalidRefreshTokenException,
    UsersServiceUnavailableException,
    OTPServiceUnavailableException,
    OTPVerificationRequiredException,
    InvalidOTPException,
    JANOServiceUnavailableException,
    PasswordPolicyViolationException,
    RateLimitExceededException,
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
    "JANOServiceUnavailableException",
    "PasswordPolicyViolationException",
    "RateLimitExceededException",
]
