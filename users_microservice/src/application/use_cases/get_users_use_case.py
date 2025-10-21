"""Get Users Use Case - Application layer (List all users)."""
from typing import Dict, List, Any
from uuid import UUID

from src.application.dtos import UserResponse
from src.core.ports.repository_ports import UserRepositoryPort


class GetUsersUseCase:
    """Use case for listing all users with pagination."""

    def __init__(self, repository: UserRepositoryPort):
        """
        Initialize GetUsersUseCase.
        
        Args:
            repository: UserRepositoryPort implementation
        """
        self.repository = repository

    async def execute(
        self,
        page: int = 1,
        size: int = 10,
        role: str = None,
        active_only: bool = False,
    ) -> Dict[str, Any]:
        """
        List all users with pagination.
        
        Args:
            page: Page number (starting from 1)
            size: Number of items per page
            role: Optional role filter
            active_only: If True, only return active users
            
        Returns:
            Dictionary with:
                - items: List of UserResponse objects
                - total: Total number of users
                - page: Current page
                - size: Page size
                - pages: Total number of pages
        """
        # Validate page and size
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 10

        # Get users from repository
        users, total = await self.repository.list_users(
            page=page,
            size=size,
            role=role,
            active_only=active_only,
        )

        # Convert to UserResponse objects
        items = [UserResponse(**user) for user in users]

        # Calculate total pages
        pages = (total + size - 1) // size if total > 0 else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }
