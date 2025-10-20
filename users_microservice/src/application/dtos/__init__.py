"""Data Transfer Objects for Users Microservice.

DTOs define the contract between layers and external services.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from typing import Optional
from datetime import datetime


# ============================================================================
# Internal DTOs (for inter-service communication)
# ============================================================================

class ValidateCredentialsRequest(BaseModel):
    """Request to validate user credentials."""
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }


class ValidateCredentialsByEmailRequest(BaseModel):
    """Request to validate user credentials by email."""
    email: EmailStr
    password: str = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@siata.gov.co",
                "password": "admin123"
            }
        }


class ValidateCredentialsResponse(BaseModel):
    """Response with validated user data."""
    id: UUID
    username: str
    email: str
    role: str
    team_name: Optional[str] = None
    is_active: bool
    permissions: list[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "admin",
                "email": "admin@siata.gov.co",
                "role": "root",
                "team_name": None,
                "is_active": True,
                "permissions": ["read", "write", "update", "disable"]
            }
        }


# ============================================================================
# User CRUD DTOs (ROOT protected)
# ============================================================================

class UserResponse(BaseModel):
    """Response with user data (no password)."""
    id: UUID
    username: str
    email: str
    name: str
    last_name: str
    role: str
    team_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "external_user",
                "email": "external@company.com",
                "name": "External",
                "last_name": "User",
                "role": "external",
                "team_name": None,
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class CreateUserRequest(BaseModel):
    """Request to create a new user (only ROOT can do this)."""
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=150)
    last_name: str = Field(..., min_length=1, max_length=150)
    role: str = Field(..., pattern="^(root|external|user_siata|admin)$")
    team_name: Optional[str] = Field(None, max_length=100)
    
    @validator('team_name')
    def validate_team_name(cls, v, values):
        """Team name is optional for admin and required for user_siata role."""
        if values.get('role') == 'user_siata' and not v:
            raise ValueError('team_name is required for user_siata role')
        if values.get('role') not in ['user_siata', 'admin'] and v:
            raise ValueError('team_name should only be set for user_siata or admin roles')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "monitoring_user",
                "email": "monitoring@siata.gov.co",
                "password": "SecureP@ssw0rd",
                "name": "Monitoring",
                "last_name": "Team",
                "role": "user_siata",
                "team_name": "monitoring"
            }
        }


class CreateUserResponse(BaseModel):
    """Response after creating a user."""
    id: UUID
    username: str
    email: str
    message: str = "User created successfully"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "monitoring_user",
                "email": "monitoring@siata.gov.co",
                "message": "User created successfully"
            }
        }


class UpdateUserRequest(BaseModel):
    """Request to update user data (only ROOT can do this)."""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    last_name: Optional[str] = Field(None, min_length=1, max_length=150)
    team_name: Optional[str] = Field(None, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "new_email@siata.gov.co",
                "name": "Updated Name"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request to change user password."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Verify that new password and confirmation match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldP@ssw0rd",
                "new_password": "NewP@ssw0rd123",
                "confirm_password": "NewP@ssw0rd123"
            }
        }


class UpdateRoleRequest(BaseModel):
    """Request to update user role (only ROOT can do this)."""
    role: str = Field(..., pattern="^(root|external|user_siata|admin)$")
    team_name: Optional[str] = Field(None, max_length=100)
    
    @validator('team_name')
    def validate_team_name(cls, v, values):
        """Team name is optional for admin and required for user_siata role."""
        if values.get('role') == 'user_siata' and not v:
            raise ValueError('team_name is required for user_siata role')
        if values.get('role') not in ['user_siata', 'admin'] and v:
            raise ValueError('team_name should only be set for user_siata or admin roles')
        return v


class PaginatedUsersResponse(BaseModel):
    """Paginated response for user list."""
    items: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 10,
                "pages": 10
            }
        }


class UserPermissionsResponse(BaseModel):
    """Response with user permissions."""
    user_id: UUID
    role: str
    team_name: Optional[str]
    permissions: list[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "root",
                "team_name": None,
                "permissions": ["read", "write", "update", "disable"]
            }
        }


__all__ = [
    "ValidateCredentialsRequest",
    "ValidateCredentialsByEmailRequest",
    "ValidateCredentialsResponse",
    "UserResponse",
    "CreateUserRequest",
    "CreateUserResponse",
    "UpdateUserRequest",
    "ChangePasswordRequest",
    "UpdateRoleRequest",
    "PaginatedUsersResponse",
    "UserPermissionsResponse",
]
