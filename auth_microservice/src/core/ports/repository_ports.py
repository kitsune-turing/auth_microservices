"""Domain ports (interfaces) for auth_microservice.

Following hexagonal architecture, ports define contracts that adapters must implement.
This keeps the domain layer independent of external services and frameworks.
"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime

from src.core.domain.entity import AuthToken, Session


# ============================================================================
# Repository Ports
# ============================================================================

class AuthTokenRepositoryPort(ABC):
    """Port for authentication token persistence."""
    
    @abstractmethod
    async def save(self, token: AuthToken) -> AuthToken:
        """Save a token to storage."""
        pass
    
    @abstractmethod
    async def get_by_id(self, token_id: UUID) -> Optional[AuthToken]:
        """Retrieve token by ID."""
        pass
    
    @abstractmethod
    async def get_by_token_string(self, token_string: str) -> Optional[AuthToken]:
        """Retrieve token by its string value."""
        pass
    
    @abstractmethod
    async def revoke_token(self, token_id: UUID) -> bool:
        """Revoke a specific token."""
        pass
    
    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """Revoke all tokens for a user."""
        pass


class SessionRepositoryPort(ABC):
    """Port for session persistence."""
    
    @abstractmethod
    async def save(self, session: Session) -> Session:
        """Save a session to storage."""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """Retrieve session by ID."""
        pass
    
    @abstractmethod
    async def get_active_sessions_for_user(self, user_id: UUID) -> list[Session]:
        """Get all active sessions for a user."""
        pass
    
    @abstractmethod
    async def end_session(self, session_id: UUID) -> bool:
        """End a specific session."""
        pass
    
    @abstractmethod
    async def end_all_user_sessions(self, user_id: UUID) -> int:
        """End all sessions for a user."""
        pass


# ============================================================================
# External Service Ports
# ============================================================================

class UserServicePort(ABC):
    """Port for user service integration."""
    
    @abstractmethod
    async def validate_credentials(self, username: str, password: str) -> Optional[dict]:
        """
        Validate user credentials.
        
        Returns:
            User data dict with id, username, role, etc. if valid, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[dict]:
        """Retrieve user information by ID."""
        pass
    
    @abstractmethod
    async def get_user_permissions(self, user_id: UUID, role: str) -> list[str]:
        """Get list of permissions for a user based on their role."""
        pass


class OtpServicePort(ABC):
    """Port for OTP service integration."""
    
    @abstractmethod
    async def generate_otp(self, user_id: UUID, channel: str = "email") -> dict:
        """
        Generate and send OTP to user.
        
        Args:
            user_id: User's unique identifier
            channel: Delivery channel (email, sms)
        
        Returns:
            Dict with otp_id, expires_at, etc.
        """
        pass
    
    @abstractmethod
    async def validate_otp(self, user_id: UUID, otp_code: str) -> bool:
        """
        Validate an OTP code.
        
        Args:
            user_id: User's unique identifier
            otp_code: The OTP code to validate
        
        Returns:
            True if valid, False otherwise
        """
        pass


# ============================================================================
# Token Service Port
# ============================================================================

class TokenServicePort(ABC):
    """Port for JWT token generation and validation."""
    
    @abstractmethod
    def generate_access_token(self, user_id: UUID, role: str, permissions: list[str]) -> str:
        """Generate an access token with user claims."""
        pass
    
    @abstractmethod
    def generate_refresh_token(self, user_id: UUID) -> str:
        """Generate a refresh token."""
        pass
    
    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token."""
        pass
    
    @abstractmethod
    def get_token_expiry(self, token: str) -> datetime:
        """Get expiration datetime from token."""
        pass


__all__ = [
    "AuthTokenRepositoryPort",
    "SessionRepositoryPort",
    "UserServicePort",
    "OtpServicePort",
    "TokenServicePort",
]
