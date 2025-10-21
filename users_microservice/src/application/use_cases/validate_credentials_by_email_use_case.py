"""Validate Credentials By Email Use Case."""
import logging
from typing import Optional

from src.core.ports.repository_ports import UserRepositoryPort, PasswordServicePort
from src.core.domain.exceptions.user_exceptions import InvalidCredentialsException
from src.core.domain.value_objects import UserRole

logger = logging.getLogger(__name__)


class ValidateCredentialsByEmailUseCase:
    """Use case for validating user credentials using email"""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_service: PasswordServicePort
    ):
        self.user_repository = user_repository
        self.password_service = password_service
    
    async def execute(self, email: str, password: str) -> dict:
        """
        Validate user credentials using email
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            dict: User data including id, username, email, role, is_active, permissions
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        logger.info(f"Validating credentials for email: {email}")
        
        # Get user by email (returns dict with password_hash included)
        user = await self.user_repository.get_user_by_email(email)
        
        if not user:
            logger.warning(f"User not found with email: {email}")
            raise InvalidCredentialsException("Invalid email or password")
        
        # Check if user is active
        if user.get('status') != 'active':
            logger.warning(f"User is inactive: {email}")
            raise InvalidCredentialsException("User account is disabled")
        
        # Verify password using password_hash from dict
        password_hash = user.get('password_hash', '')
        if not self.password_service.verify_password(password, password_hash):
            logger.warning(f"Invalid password for email: {email}")
            raise InvalidCredentialsException("Invalid email or password")
        
        logger.info(f"Credentials validated successfully for email: {email}")
        
        # Get permissions based on role
        user_role = UserRole(user['role'])
        permissions = user_role.default_permissions
        
        # Return user data compatible with ValidateCredentialsResponse
        # (without password_hash for security)
        return {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "team_name": user.get('team_name'),
            "is_active": user.get('status') == 'active',
            "permissions": permissions
        }
