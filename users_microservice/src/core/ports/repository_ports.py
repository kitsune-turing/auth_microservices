"""Repository Port Interfaces for Users Microservice.

Following hexagonal architecture, these interfaces define contracts
that infrastructure layer must implement.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID


class UserRepositoryPort(ABC):
    """Port interface for user repository operations."""
    
    @abstractmethod
    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        name: str,
        last_name: str,
        role: str,
        team_id: Optional[UUID] = None,
    ) -> UUID:
        """Create a new user and return the user ID."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[dict]:
        """Get user by ID. Returns dict with user data or None."""
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username. Returns dict with user data or None."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email. Returns dict with user data or None."""
        pass
    
    @abstractmethod
    async def update_user(
        self,
        user_id: UUID,
        email: Optional[str] = None,
        name: Optional[str] = None,
        last_name: Optional[str] = None,
        team_id: Optional[UUID] = None,
    ) -> Optional[dict]:
        """Update user data. Returns updated user dict or None if failed."""
        pass
    
    @abstractmethod
    async def update_password(self, user_id: UUID, password_hash: str) -> bool:
        """Update user password hash. Returns True if successful."""
        pass
    
    @abstractmethod
    async def update_role(
        self,
        user_id: UUID,
        role: str,
        team_id: Optional[UUID] = None,
    ) -> bool:
        """Update user role and team. Returns True if successful."""
        pass
    
    @abstractmethod
    async def disable_user(self, user_id: UUID) -> Optional[dict]:
        """Disable user (soft delete). Returns updated user dict or None."""
        pass
    
    @abstractmethod
    async def enable_user(self, user_id: UUID) -> Optional[dict]:
        """Enable user. Returns updated user dict or None."""
        pass
    
    @abstractmethod
    async def list_users(
        self,
        page: int = 1,
        size: int = 10,
        role: Optional[str] = None,
        active_only: bool = False,
    ) -> tuple[List[dict], int]:
        """
        List users with pagination and filters.
        Returns tuple of (users_list, total_count).
        """
        pass
    
    @abstractmethod
    async def user_exists(self, username: str = None, email: str = None) -> bool:
        """Check if user exists by username or email."""
        pass


class PasswordServicePort(ABC):
    """Port interface for password hashing operations."""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password using BCrypt."""
        pass
    
    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        pass


__all__ = ["UserRepositoryPort", "PasswordServicePort"]
