"""Centralized error codes and messages for auth_microservice.

This module provides a standardized error catalog following best practices.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AuthErrorCode(str, Enum):
    """Centralized error codes for auth_microservice."""
    
    # Authentication errors (1000-1099)
    INVALID_CREDENTIALS = "AUTH_1001"
    USER_NOT_FOUND = "AUTH_1002"
    USER_INACTIVE = "AUTH_1003"
    USER_LOCKED = "AUTH_1004"
    
    # Token errors (1100-1199)
    TOKEN_EXPIRED = "AUTH_1101"
    TOKEN_INVALID = "AUTH_1102"
    TOKEN_REVOKED = "AUTH_1103"
    TOKEN_MALFORMED = "AUTH_1104"
    REFRESH_TOKEN_INVALID = "AUTH_1105"
    
    # OTP errors (1200-1299)
    OTP_INVALID = "AUTH_1201"
    OTP_EXPIRED = "AUTH_1202"
    OTP_MAX_ATTEMPTS = "AUTH_1203"
    OTP_GENERATION_FAILED = "AUTH_1204"
    
    # Authorization errors (1300-1399)
    INSUFFICIENT_PERMISSIONS = "AUTH_1301"
    ROLE_NOT_FOUND = "AUTH_1302"
    ACCESS_DENIED = "AUTH_1303"
    
    # Service integration errors (1400-1499)
    USER_SERVICE_UNAVAILABLE = "AUTH_1401"
    OTP_SERVICE_UNAVAILABLE = "AUTH_1402"
    EXTERNAL_SERVICE_ERROR = "AUTH_1403"
    
    # Validation errors (1500-1599)
    INVALID_INPUT = "AUTH_1501"
    MISSING_REQUIRED_FIELD = "AUTH_1502"
    INVALID_FORMAT = "AUTH_1503"
    
    # Internal errors (1900-1999)
    DATABASE_ERROR = "AUTH_1901"
    INTERNAL_SERVER_ERROR = "AUTH_1999"


@dataclass
class ErrorDetail:
    """Structured error detail."""
    
    code: AuthErrorCode
    message: str
    user_message: Optional[str] = None  # User-friendly message
    hint: Optional[str] = None  # Suggestion for resolution
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "code": self.code.value,
            "message": self.message,
        }
        if self.user_message:
            result["user_message"] = self.user_message
        if self.hint:
            result["hint"] = self.hint
        return result


class AuthErrorList:
    """Centralized error catalog for auth_microservice."""
    
    # Authentication errors
    INVALID_CREDENTIALS = ErrorDetail(
        code=AuthErrorCode.INVALID_CREDENTIALS,
        message="The provided username or password is incorrect",
        user_message="Invalid credentials. Please check your username and password.",
        hint="Ensure credentials are correct and account is active"
    )
    
    USER_NOT_FOUND = ErrorDetail(
        code=AuthErrorCode.USER_NOT_FOUND,
        message="User account not found",
        user_message="We couldn't find an account with those credentials.",
    )
    
    USER_INACTIVE = ErrorDetail(
        code=AuthErrorCode.USER_INACTIVE,
        message="User account is inactive or disabled",
        user_message="Your account is inactive. Please contact support.",
    )
    
    # Token errors
    TOKEN_EXPIRED = ErrorDetail(
        code=AuthErrorCode.TOKEN_EXPIRED,
        message="Authentication token has expired",
        user_message="Your session has expired. Please log in again.",
        hint="Use refresh token to obtain a new access token"
    )
    
    TOKEN_INVALID = ErrorDetail(
        code=AuthErrorCode.TOKEN_INVALID,
        message="Invalid or malformed authentication token",
        user_message="Authentication failed. Please log in again.",
    )
    
    TOKEN_REVOKED = ErrorDetail(
        code=AuthErrorCode.TOKEN_REVOKED,
        message="Token has been revoked",
        user_message="Your session has been terminated. Please log in again.",
    )
    
    REFRESH_TOKEN_INVALID = ErrorDetail(
        code=AuthErrorCode.REFRESH_TOKEN_INVALID,
        message="Invalid or expired refresh token",
        user_message="Cannot refresh session. Please log in again.",
    )
    
    # OTP errors
    OTP_INVALID = ErrorDetail(
        code=AuthErrorCode.OTP_INVALID,
        message="Invalid OTP code provided",
        user_message="The code you entered is incorrect.",
        hint="Check your email/SMS for the correct code"
    )
    
    OTP_EXPIRED = ErrorDetail(
        code=AuthErrorCode.OTP_EXPIRED,
        message="OTP code has expired",
        user_message="The code has expired. Please request a new one.",
    )
    
    OTP_GENERATION_FAILED = ErrorDetail(
        code=AuthErrorCode.OTP_GENERATION_FAILED,
        message="Failed to generate OTP",
        user_message="Unable to send verification code. Please try again.",
    )
    
    # Authorization errors
    INSUFFICIENT_PERMISSIONS = ErrorDetail(
        code=AuthErrorCode.INSUFFICIENT_PERMISSIONS,
        message="User lacks required permissions for this operation",
        user_message="You don't have permission to perform this action.",
    )
    
    ACCESS_DENIED = ErrorDetail(
        code=AuthErrorCode.ACCESS_DENIED,
        message="Access denied to requested resource",
        user_message="Access denied.",
    )
    
    # Service errors
    USER_SERVICE_UNAVAILABLE = ErrorDetail(
        code=AuthErrorCode.USER_SERVICE_UNAVAILABLE,
        message="User service is currently unavailable",
        user_message="Service temporarily unavailable. Please try again later.",
    )
    
    OTP_SERVICE_UNAVAILABLE = ErrorDetail(
        code=AuthErrorCode.OTP_SERVICE_UNAVAILABLE,
        message="OTP service is currently unavailable",
        user_message="Unable to send verification code. Please try again later.",
    )
    
    # Validation errors
    INVALID_INPUT = ErrorDetail(
        code=AuthErrorCode.INVALID_INPUT,
        message="Invalid input data provided",
        user_message="Please check your input and try again.",
    )
    
    # Internal errors
    DATABASE_ERROR = ErrorDetail(
        code=AuthErrorCode.DATABASE_ERROR,
        message="Database operation failed",
        user_message="A technical error occurred. Please try again.",
    )
    
    INTERNAL_SERVER_ERROR = ErrorDetail(
        code=AuthErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected internal error occurred",
        user_message="Something went wrong. Please try again later.",
    )


__all__ = [
    "AuthErrorCode",
    "ErrorDetail",
    "AuthErrorList",
]
