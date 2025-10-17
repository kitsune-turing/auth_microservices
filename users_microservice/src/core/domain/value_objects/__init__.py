"""Value Objects for Users Domain.

Immutable objects that represent domain concepts without identity.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class UserRole(str, Enum):
    """User roles in the system."""
    ROOT = "root"
    EXTERNAL = "external"
    USER_SIATA = "user_siata"
    
    @property
    def default_permissions(self) -> list[str]:
        """Get default permissions for this role."""
        if self == UserRole.ROOT:
            return ["read", "write", "update", "disable"]
        
        elif self == UserRole.EXTERNAL:
            return ["read"]
            
        elif self == UserRole.USER_SIATA:
            return ["read", "write", "update"]
        return []
    
    def full_role_name(self, team_name: Optional[str] = None) -> str:
        """Get full role name with team if applicable."""
        if self == UserRole.USER_SIATA and team_name:
            return f"user_siata.{team_name}"
        return self.value


@dataclass(frozen=True)
class UserPermissions:
    """User permissions value object."""
    role: UserRole
    team_name: Optional[str] = None
    custom_permissions: Optional[list[str]] = None
    
    @property
    def all_permissions(self) -> list[str]:
        """Get all permissions (default + custom)."""
        perms = self.role.default_permissions
        if self.custom_permissions:
            perms.extend(self.custom_permissions)
        return list(set(perms))  # Remove duplicates
    
    @property
    def full_role(self) -> str:
        """Get full role string."""
        return self.role.full_role_name(self.team_name)
    
    def can(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.all_permissions


__all__ = ["UserRole", "UserPermissions"]
