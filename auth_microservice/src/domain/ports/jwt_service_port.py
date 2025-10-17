"""JWT Service Port Interface.

Defines the contract for JWT token operations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from datetime import timedelta, datetime

from ..value_objects.token_payload import TokenPayload


class JWTServicePort(ABC):
    """Port interface for JWT operations."""
    
    @abstractmethod
    def create_access_token(
        self,
        user_id: str,
        username: str,
        role: str,
        permissions: list[str],
        team_name: str | None = None,
        expires_delta: timedelta | None = None,
        token_id: str | None = None,
    ) -> Tuple[str, str, datetime]:
        """
        Create a new access token.
        
        Args:
            user_id: User ID (UUID as string)
            username: Username
            role: User role
            permissions: List of permissions
            team_name: Team name (optional)
            expires_delta: Custom expiration time (optional)
            token_id: Optional token ID (generated if not provided)
            
        Returns:
            Tuple of (token_string, token_id, expires_at)
        """
        pass
    
    @abstractmethod
    def create_refresh_token(
        self,
        user_id: str,
        username: str,
        expires_delta: timedelta | None = None,
        token_id: str | None = None,
    ) -> Tuple[str, str, datetime]:
        """
        Create a new refresh token.
        
        Args:
            user_id: User ID (UUID as string)
            username: Username
            expires_delta: Custom expiration time (optional)
            token_id: Optional token ID (generated if not provided)
            
        Returns:
            Tuple of (token_string, token_id, expires_at)
        """
        pass
    
    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        """
        Decode and validate a JWT token.
        
        Args:
            token: Encoded JWT token string
            
        Returns:
            TokenPayload with decoded data
            
        Raises:
            TokenExpiredException: If token is expired
            InvalidTokenException: If token is invalid
        """
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> bool:
        """
        Verify if a token is valid (not expired, valid signature).
        
        Args:
            token: Encoded JWT token string
            
        Returns:
            True if token is valid, False otherwise
        """
        pass


__all__ = ["JWTServicePort"]
