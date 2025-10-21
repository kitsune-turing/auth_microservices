"""Enable User Use Case - Application layer."""
from uuid import UUID

from src.core.ports.repository_ports import UserRepositoryPort


class EnableUserUseCase:
    """Use case for enabling a user account."""

    def __init__(self, repository: UserRepositoryPort):
        """
        Initialize EnableUserUseCase.
        
        Args:
            repository: UserRepositoryPort implementation
        """
        self.repository = repository

    async def execute(self, user_id: UUID) -> dict:
        """
        Enable a user account (set status to 'active').
        
        Args:
            user_id: UUID of the user to enable
            
        Returns:
            Dictionary with success message
            
        Raises:
            ValueError: If user not found
        """
        # Check if user exists
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Enable user (set status to active)
        updated_user = await self.repository.enable_user(user_id)

        if not updated_user:
            raise ValueError(f"Failed to enable user {user_id}")

        return {
            "message": f"User {user_id} enabled successfully",
            "user_id": str(user_id),
            "status": updated_user.get("status"),
        }
