"""Value Objects for auth domain.

Value Objects are immutable objects defined by their attributes rather than identity.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    """User roles with associated permissions."""
    
    ROOT = "root"
    EXTERNAL = "external"
    USER_SIATA = "user_siata"  # Base role, teams specified via team_name
    
    @property
    def can_delete(self) -> bool:
        """Root cannot delete, only disable."""
        return False
    
    @property
    def can_write(self) -> bool:
        """Check if role has write permissions."""
        return self in [UserRole.ROOT, UserRole.USER_SIATA]
    
    @property
    def can_read(self) -> bool:
        """All roles can read."""
        return True


@dataclass(frozen=True)
class Credentials:
    """User credentials value object."""
    
    username: str
    password: str
    
    def __post_init__(self):
        """Validate credentials."""
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty")
        if not self.password or len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")


@dataclass(frozen=True)
class UserClaims:
    """JWT claims for a user."""
    
    user_id: str
    username: str
    role: UserRole
    team_name: Optional[str] = None  # For user_siata.#team_name
    permissions: Optional[list[str]] = None
    
    def __post_init__(self):
        """Initialize permissions list if None."""
        if self.permissions is None:
            object.__setattr__(self, 'permissions', [])
    
    @property
    def full_role(self) -> str:
        """Get full role string with team if applicable."""
        if self.role == UserRole.USER_SIATA and self.team_name:
            return f"user_siata.{self.team_name}"
        return self.role.value
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JWT encoding."""
        return {
            "sub": self.user_id,
            "username": self.username,
            "role": self.full_role,
            "permissions": self.permissions,
        }


@dataclass(frozen=True)
class OtpRequest:
    """OTP verification request."""
    
    user_id: str
    otp_code: str
    
    def __post_init__(self):
        """Validate OTP request."""
        if not self.otp_code or len(self.otp_code) != 6:
            raise ValueError("OTP code must be 6 digits")
        if not self.otp_code.isdigit():
            raise ValueError("OTP code must contain only digits")


@dataclass(frozen=True)
class ClientInfo:
    """Client information for session tracking."""
    
    ip_address: str
    user_agent: str
    
    def __post_init__(self):
        """Validate client info."""
        if not self.ip_address:
            raise ValueError("IP address cannot be empty")
        if not self.user_agent:
            raise ValueError("User agent cannot be empty")


__all__ = [
    "UserRole",
    "Credentials",
    "UserClaims",
    "OtpRequest",
    "ClientInfo",
]
