"""Token Payload Value Object.

Represents the payload data contained in a JWT token.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """JWT Token Payload."""
    
    sub: str = Field(..., description="Subject (user_id)")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role (ROOT, EXTERNAL, USER_SIATA)")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    team_name: Optional[str] = Field(None, description="Team name for USER_SIATA")
    iat: int = Field(..., description="Issued at (timestamp)")
    exp: int = Field(..., description="Expiration time (timestamp)")
    token_type: str = Field(..., description="Token type (access or refresh)")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "sub": "123e4567-e89b-12d3-a456-426614174000",
                "username": "admin",
                "role": "ROOT",
                "permissions": ["create_user", "read_user", "update_user"],
                "team_name": "SIATA",
                "iat": 1697500000,
                "exp": 1697503600,
                "token_type": "access"
            }
        }
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow().timestamp() > self.exp
    
    def is_access_token(self) -> bool:
        """Check if this is an access token."""
        return self.token_type == "access"
    
    def is_refresh_token(self) -> bool:
        """Check if this is a refresh token."""
        return self.token_type == "refresh"


__all__ = ["TokenPayload"]
