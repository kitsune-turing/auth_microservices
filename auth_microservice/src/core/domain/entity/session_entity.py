"""Session entity for domain layer."""
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from typing import Optional


class Session:
    """
    Entity representing a user session.
    Encapsulates business logic for session management and lifecycle.
    """

    def __init__(
        self,
        user_id: UUID,
        access_token_id: UUID,
        ip_address: str,
        user_agent: str,
        session_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        last_activity: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        active: bool = True,
    ) -> None:
        """
        Initialize a user session.
        
        Args:
            user_id: UUID of the user
            access_token_id: UUID of the associated access token
            ip_address: IP address of the client
            user_agent: User agent string
            session_id: Optional UUID for the session (generated if not provided)
            created_at: Optional creation timestamp (defaults to now)
            last_activity: Optional last activity timestamp (defaults to now)
            expires_at: Optional expiration timestamp (defaults to now + 7 days)
            active: Whether the session is active
        """
        if not isinstance(user_id, UUID):
            raise TypeError(f"user_id must be UUID, got {type(user_id)}")
        
        if not isinstance(access_token_id, UUID):
            raise TypeError(f"access_token_id must be UUID, got {type(access_token_id)}")
        
        if not isinstance(ip_address, str) or not ip_address.strip():
            raise ValueError("ip_address must be a non-empty string")
        
        if not isinstance(user_agent, str):
            raise ValueError("user_agent must be a string")
        
        self._id = session_id or uuid4()
        self._user_id = user_id
        self._access_token_id = access_token_id
        self._ip_address = ip_address
        self._user_agent = user_agent
        self._created_at = created_at or datetime.now(timezone.utc)
        self._last_activity = last_activity or datetime.now(timezone.utc)
        self._expires_at = expires_at or (datetime.now(timezone.utc) + timedelta(days=7))
        self._active = active
    

    # Properties
    @property
    def id(self) -> UUID:
        """Get session ID."""
        return self._id
    
    @property
    def user_id(self) -> UUID:
        """Get user ID."""
        return self._user_id
    
    @property
    def access_token_id(self) -> UUID:
        """Get associated access token ID."""
        return self._access_token_id
    
    @property
    def ip_address(self) -> str:
        """Get client IP address."""
        return self._ip_address
    
    @property
    def user_agent(self) -> str:
        """Get user agent string."""
        return self._user_agent
    
    @property
    def created_at(self) -> datetime:
        """Get creation datetime."""
        return self._created_at
    
    @property
    def last_activity(self) -> datetime:
        """Get last activity datetime."""
        return self._last_activity
    
    @property
    def expires_at(self) -> datetime:
        """Get expiration datetime."""
        return self._expires_at
    
    @property
    def active(self) -> bool:
        """Check if session is active."""
        return self._active
    
    # Domain Methods
    def is_expired(self) -> bool:
        """
        Check if the session has expired.
        
        Returns:
            True if current time is past expiration, False otherwise
        """
        now = datetime.now(timezone.utc)
        return now > self._expires_at
    
    def is_valid(self) -> bool:
        """
        Check if the session is valid.
        
        A session is valid if it's active and not expired.
        
        Returns:
            True if session is valid, False otherwise
        """
        return self._active and not self.is_expired()
    
    def update_activity(self) -> None:
        """
        Update the last activity timestamp.
        
        Called when the session receives a new request to keep it alive.
        """
        self._last_activity = datetime.now(timezone.utc)
    
    def end_session(self) -> None:
        """
        End the session.
        
        Marks the session as inactive, effectively logging out the user.
        """
        self._active = False
    
    def __repr__(self) -> str:
        """String representation of the session."""
        return (
            f"Session(id={self._id}, user_id={self._user_id}, "
            f"active={self._active}, expires_at={self._expires_at})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on session ID."""
        if not isinstance(other, Session):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on session ID."""
        return hash(self._id)