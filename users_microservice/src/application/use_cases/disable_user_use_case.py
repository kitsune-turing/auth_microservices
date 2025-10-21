"""Disable User Use Case - Application layer."""
from uuid import UUID

from src.core.ports.repository_ports import UserRepositoryPort


class DisableUserUseCase:
    """Use case for disabling a user account."""

    def __init__(self, repository: UserRepositoryPort):
        """
        Initialize DisableUserUseCase.
        
        Args:
            repository: UserRepositoryPort implementation
        """
        self.repository = repository

    async def execute(self, user_id: UUID) -> dict:
        """
        Disable a user account (set status to 'inactive').
        
        Args:
            user_id: UUID of the user to disable
            
        Returns:
            Dictionary with success message
            
        Raises:
            ValueError: If user not found
        """
        # Check if user exists
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Disable user (set status to inactive)
        updated_user = await self.repository.disable_user(user_id)

        if not updated_user:
            raise ValueError(f"Failed to disable user {user_id}")

        return {
            "message": f"User {user_id} disabled successfully",
            "user_id": str(user_id),
            "status": updated_user.get("status"),
        }
