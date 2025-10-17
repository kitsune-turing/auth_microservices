"""Authentication entities for domain layer."""
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional


class TokenType(str, Enum):
    """Enumeration of token types."""
    ACCESS = "access"
    REFRESH = "refresh"
    SESSION = "session"


class AuthToken:
    """
    Entity representing an authentication token.
    
    Encapsulates business logic for JWT token management.
    """
    
    def __init__(
        self,
        user_id: UUID,
        token_type: TokenType,
        token_string: str,
        expires_at: datetime,
        token_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        revoked: bool = False,
    ) -> None:
        """
        Initialize an authentication token.
        
        Args:
            user_id: UUID of the user who owns this token
            token_type: Type of token (ACCESS, REFRESH, SESSION)
            token_string: The JWT token string
            expires_at: When the token expires
            token_id: Optional UUID for the token (generated if not provided)
            created_at: Optional creation timestamp (defaults to now)
            revoked: Whether the token has been revoked
        """
        if not isinstance(user_id, UUID):
            raise TypeError(f"user_id must be UUID, got {type(user_id)}")
        
        if not isinstance(token_type, TokenType):
            raise TypeError(f"token_type must be TokenType, got {type(token_type)}")
        
        if not isinstance(token_string, str) or not token_string.strip():
            raise ValueError("token_string must be a non-empty string")
        
        if not isinstance(expires_at, datetime):
            raise TypeError("expires_at must be a datetime")
        
        self._id = token_id or uuid4()
        self._user_id = user_id
        self._token_type = token_type
        self._token_string = token_string
        self._expires_at = expires_at
        self._created_at = created_at or datetime.now(timezone.utc)
        self._revoked = revoked
    
    # Properties
    @property
    def id(self) -> UUID:
        """Get token ID."""
        return self._id
    
    @property
    def user_id(self) -> UUID:
        """Get user ID."""
        return self._user_id
    
    @property
    def token_type(self) -> TokenType:
        """Get token type."""
        return self._token_type
    
    @property
    def token_string(self) -> str:
        """Get token string."""
        return self._token_string
    
    @property
    def expires_at(self) -> datetime:
        """Get expiration datetime."""
        return self._expires_at
    
    @property
    def created_at(self) -> datetime:
        """Get creation datetime."""
        return self._created_at
    
    @property
    def revoked(self) -> bool:
        """Check if token is revoked."""
        return self._revoked
    
    # Domain Methods
    def is_expired(self) -> bool:
        """
        Check if the token has expired.
        
        Returns:
            True if current time is past expiration, False otherwise
        """
        now = datetime.now(timezone.utc)
        return now > self._expires_at
    
    def is_valid(self) -> bool:
        """
        Check if the token is valid.
        
        A token is valid if it's not expired and not revoked.
        
        Returns:
            True if token is valid, False otherwise
        """
        return not self.is_expired() and not self._revoked
    
    def revoke(self) -> None:
        """
        Revoke the token.
        
        Marks the token as revoked, making it invalid immediately.
        """
        self._revoked = True
    
    def __repr__(self) -> str:
        """String representation of the token."""
        return (
            f"AuthToken(id={self._id}, user_id={self._user_id}, "
            f"type={self._token_type}, revoked={self._revoked})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on token ID."""
        if not isinstance(other, AuthToken):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on token ID."""
        return hash(self._id)