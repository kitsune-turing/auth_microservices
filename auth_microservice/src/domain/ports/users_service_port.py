"""Users Service Port Interface.

Defines the contract for communication with users_microservice.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class UsersServicePort(ABC):
    """Port interface for users_microservice communication."""
    
    @abstractmethod
    async def validate_credentials(
        self,
        username: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Validate user credentials via users_microservice.
        
        Args:
            username: Username
            password: Password (plain text, will be validated by users service)
            
        Returns:
            Dict with user data:
            {
                "is_valid": bool,
                "user_id": str,
                "username": str,
                "email": str,
                "role": str,
                "permissions": list[str],
                "team_name": str | None
            }
            
        Raises:
            UsersServiceUnavailableException: If service is unavailable
            InvalidCredentialsException: If credentials are invalid
        """
        pass
    
    @abstractmethod
    async def validate_credentials_by_email(
        self,
        email: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Validate user credentials by email via users_microservice.
        
        Args:
            email: User email
            password: Password (plain text, will be validated by users service)
            
        Returns:
            Dict with user data or None if invalid
            
        Raises:
            UsersServiceUnavailableException: If service is unavailable
        """
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID.
        
        Args:
            user_id: User ID (UUID as string)
            
        Returns:
            Dict with user data or None if not found
            
        Raises:
            UsersServiceUnavailableException: If service is unavailable
        """
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by email.
        
        Args:
            email: User email
            
        Returns:
            Dict with user data or None if not found
            
        Raises:
            UsersServiceUnavailableException: If service is unavailable
        """
        pass


__all__ = ["UsersServicePort"]
