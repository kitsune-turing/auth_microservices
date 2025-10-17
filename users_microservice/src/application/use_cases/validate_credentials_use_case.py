"""Validate Credentials Use Case.

This is the CRITICAL use case that auth_microservice depends on.
"""
import logging
from typing import Optional

from src.core.ports.repository_ports import UserRepositoryPort, PasswordServicePort
from src.core.domain.value_objects import UserRole
from src.application.dtos import ValidateCredentialsResponse

logger = logging.getLogger(__name__)


class ValidateCredentialsUseCase:
    """
    Use case for validating user credentials.
    
    This is called by auth_microservice during login flow.
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_service: PasswordServicePort,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
    
    async def execute(
        self,
        username: str,
        password: str,
    ) -> Optional[ValidateCredentialsResponse]:
        """
        Validate user credentials.
        
        Args:
            username: Username to validate
            password: Plain text password
            
        Returns:
            ValidateCredentialsResponse if valid, None if invalid
            
        Raises:
            Exception if user is inactive
        """
        logger.info(f"Validating credentials for username: {username}")
        
        # 1. Get user by username
        user = await self.user_repository.get_user_by_username(username)
        
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        # 2. Check if user is active
        if not user.get('is_active', False):
            logger.warning(f"User is inactive: {username}")
            raise Exception("User account is disabled")
        
        # 3. Verify password
        password_hash = user.get('password_hash', '')
        is_valid = self.password_service.verify_password(password, password_hash)
        
        if not is_valid:
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        # 4. Get permissions based on role
        user_role = UserRole(user['role'])
        permissions = user_role.default_permissions
        
        # 5. Build response
        logger.info(f"Credentials validated successfully for: {username}")
        
        return ValidateCredentialsResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            role=user['role'],
            team_name=user.get('team_name'),
            is_active=user['is_active'],
            permissions=permissions,
        )


__all__ = ["ValidateCredentialsUseCase"]
