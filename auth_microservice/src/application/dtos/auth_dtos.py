"""Authentication DTOs (Data Transfer Objects).

Request and Response models for auth endpoints.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


# ============================================================================
# Error DTOs
# ============================================================================

class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    code: str = Field(..., description="Error code (e.g., AUTH_001)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    path: Optional[str] = Field(None, description="Request path that caused the error")
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "code": "AUTH_001",
                "message": "Invalid credentials",
                "details": "Username or password is incorrect",
                "timestamp": "2025-10-16T20:00:00Z",
                "path": "/auth/login"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: ErrorDetail
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "AUTH_001",
                    "message": "Invalid credentials",
                    "details": "Username or password is incorrect",
                    "timestamp": "2025-10-16T20:00:00Z",
                    "path": "/auth/login"
                }
            }
        }


# ============================================================================
# Login DTOs
# ============================================================================

class LoginRequest(BaseModel):
    """Login request model - Step 1: Validate credentials and send OTP."""
    
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "email": "admin@siata.gov.co",
                "password": "Admin123!"
            }
        }


class LoginInitResponse(BaseModel):
    """Response after initial login - OTP sent."""
    
    message: str = Field(..., description="Status message")
    email: str = Field(..., description="Masked email where OTP was sent")
    otp_id: str = Field(..., description="OTP identifier for validation")
    expires_in: int = Field(..., description="OTP expiration time in seconds")
    otp_code: Optional[str] = Field(None, description="OTP code (only in development mode)")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "message": "OTP sent to your email",
                "email": "a***n@siata.gov.co",
                "otp_id": "123e4567-e89b-12d3-a456-426614174000",
                "expires_in": 300,
                "otp_code": "123456"
            }
        }


class VerifyLoginRequest(BaseModel):
    """Verify login request - Step 2: Validate OTP and get tokens."""
    
    otp_id: str = Field(..., description="OTP identifier from login step")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    ip_address: Optional[str] = Field(default="0.0.0.0", description="Client IP address")
    user_agent: Optional[str] = Field(default="Unknown", description="Client user agent")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "otp_id": "6b267ff8-1c93-44cd-a882-acbb8cdc07e8",
                "otp_code": "123456",
                "ip_address": "192.168.1.100",
                "user_agent": "PostmanRuntime/7.32.0"
            }
        }


class TokenResponse(BaseModel):
    """Token response model."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class LoginResponse(BaseModel):
    """Login response model (extended with user info)."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    user: dict = Field(..., description="User information")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "admin",
                    "email": "admin@siata.gov.co",
                    "role": "ROOT",
                    "permissions": ["create_user", "read_user", "update_user"],
                    "team_name": "SIATA"
                }
            }
        }


# ============================================================================
# Refresh Token DTOs
# ============================================================================

class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# ============================================================================
# Current User DTOs
# ============================================================================

class CurrentUserResponse(BaseModel):
    """Current user information response."""
    
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email")
    role: str = Field(..., description="User role")
    permissions: List[str] = Field(..., description="User permissions")
    team_name: Optional[str] = Field(None, description="Team name")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "admin",
                "email": "admin@siata.gov.co",
                "role": "ROOT",
                "permissions": ["create_user", "read_user", "update_user"],
                "team_name": "SIATA"
            }
        }


__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "LoginRequest",
    "TokenResponse",
    "LoginResponse",
    "RefreshTokenRequest",
    "CurrentUserResponse",
]
