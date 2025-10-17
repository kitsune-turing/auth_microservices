"""Data Transfer Objects for Auth Microservice."""

from .auth_dtos import (
    ErrorDetail,
    ErrorResponse,
    LoginRequest,
    LoginInitResponse,
    VerifyLoginRequest,
    TokenResponse,
    LoginResponse,
    RefreshTokenRequest,
    CurrentUserResponse,
)

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "LoginRequest",
    "LoginInitResponse",
    "VerifyLoginRequest",
    "TokenResponse",
    "LoginResponse",
    "RefreshTokenRequest",
    "CurrentUserResponse",
]
