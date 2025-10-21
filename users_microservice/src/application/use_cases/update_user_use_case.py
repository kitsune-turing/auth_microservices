"""Update User Use Case - Application layer."""
from typing import Optional
from uuid import UUID

from src.application.dtos import UpdateUserRequest, UserResponse
from src.core.ports.repository_ports import UserRepositoryPort


class UpdateUserUseCase:
    """Use case for updating user information."""

    def __init__(self, repository: UserRepositoryPort):
        """
        Initialize UpdateUserUseCase.
        
        Args:
            repository: UserRepositoryPort implementation
        """
        self.repository = repository

    async def execute(
        self,
        user_id: UUID,
        request: UpdateUserRequest,
    ) -> UserResponse:
        """
        Update user information.
        
        Args:
            user_id: UUID of the user to update
            request: UpdateUserRequest with fields to update
            
        Returns:
            UserResponse with updated user data
            
        Raises:
            ValueError: If user not found or email already exists
        """
        # Check if user exists
        existing_user = await self.repository.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"User with ID {user_id} not found")

        # If email is being updated, check for duplicates
        if request.email and request.email != existing_user.get("email"):
            existing_by_email = await self.repository.get_user_by_email(request.email)
            if existing_by_email:
                raise ValueError(f"Email {request.email} is already in use")

        # Update user with individual parameters
        updated_user = await self.repository.update_user(
            user_id=user_id,
            email=request.email,
            name=request.name,
            last_name=request.last_name,
            team_id=request.team_id,
        )

        if not updated_user:
            raise ValueError(f"Failed to update user {user_id}")

        return UserResponse(**updated_user)
