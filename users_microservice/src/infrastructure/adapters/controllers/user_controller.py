"""User Controller for Users Microservice.

Handles user CRUD operations. Only ROOT users can create/modify users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.application.dtos import (
    CreateUserRequest,
    CreateUserResponse,
    UserResponse,
)
from src.application.use_cases.get_user_use_case import GetUserUseCase
from src.application.use_cases.create_user_use_case import CreateUserUseCase
from src.infrastructure.config.dependencies import (
    get_get_user_use_case,
    get_create_user_use_case,
)
from src.infrastructure.middleware import require_root_role


router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve user information by user ID. Requires ROOT role.",
    dependencies=[Depends(require_root_role)],
)
async def get_user(
    user_id: UUID,
    use_case: GetUserUseCase = Depends(get_get_user_use_case),
) -> UserResponse:
    """
    Get user by ID.
    
    Protected endpoint - Requires ROOT role.
    
    Args:
        user_id: UUID of the user
        use_case: Injected GetUserUseCase
        
    Returns:
        UserResponse with user data
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(user_id)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user. Only ROOT users can perform this operation.",
    dependencies=[Depends(require_root_role)],
)
async def create_user(
    request: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> CreateUserResponse:
    """
    Create a new user.
    
    Protected endpoint - Requires ROOT role.
    
    Args:
        request: User creation data
        use_case: Injected CreateUserUseCase
        
    Returns:
        CreateUserResponse with new user_id
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 409: Username or email already exists
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(request)
        return result
        
    except ValueError as e:
        # Duplicate username/email
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

