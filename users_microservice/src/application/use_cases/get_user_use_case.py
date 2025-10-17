"""Get User Use Case."""
import logging
from uuid import UUID
from typing import Optional

from src.core.ports.repository_ports import UserRepositoryPort
from src.application.dtos import UserResponse

logger = logging.getLogger(__name__)


class GetUserUseCase:
    """Use case for getting user by ID."""
    
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository
    
    async def execute(self, user_id: UUID) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserResponse if found, None otherwise
        """
        logger.info(f"Getting user: {user_id}")
        
        user = await self.user_repository.get_user_by_id(user_id)
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return None
        
        return UserResponse(**user)


__all__ = ["GetUserUseCase"]
