"""Get User By Email Use Case."""
import logging
from typing import Optional

from src.core.ports.repository_ports import UserRepositoryPort
from src.core.domain.exceptions.user_exceptions import UserNotFoundException

logger = logging.getLogger(__name__)


class GetUserByEmailUseCase:
    """Use case for retrieving a user by email address"""
    
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository
    
    async def execute(self, email: str) -> dict:
        """
        Get user by email address
        
        Args:
            email: User's email address
            
        Returns:
            dict: User data including id, email, first_name, last_name, role, status
            
        Raises:
            UserNotFoundException: If user with given email doesn't exist
        """
        logger.info(f"Getting user by email: {email}")
        
        user = await self.user_repository.get_user_by_email(email)
        
        if not user:
            logger.warning(f"User not found with email: {email}")
            raise UserNotFoundException(f"User with email {email} not found")
        
        logger.info(f"User found: {user['id']}")
        
        # Return user data (without password_hash for security)
        return {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "name": user['name'],
            "last_name": user['last_name'],
            "role": user['role'],
            "team_name": user.get('team_name'),
            "status": user['status'],
            "is_mfa_enabled": user.get('is_mfa_enabled', False),
            "created_at": user['created_at'].isoformat() if user.get('created_at') else None,
            "updated_at": user['updated_at'].isoformat() if user.get('updated_at') else None
        }
