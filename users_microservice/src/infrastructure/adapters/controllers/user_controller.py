"""User Controller for Users Microservice.

Handles user CRUD operations. Only ROOT users can create/modify users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.application.dtos import (
    CreateUserRequest,
    CreateUserResponse,
    UserResponse,
    UpdateUserRequest,
)
from src.application.use_cases.get_user_use_case import GetUserUseCase
from src.application.use_cases.create_user_use_case import CreateUserUseCase
from src.infrastructure.config.dependencies import (
    get_get_user_use_case,
    get_create_user_use_case,
)
from src.infrastructure.middleware import require_root_role
from src.infrastructure.adapters.jano_client import JANOValidationError


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
        HTTPException 400: Password/username doesn't meet security requirements
        HTTPException 409: Username or email already exists
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(request)
        return result
    
    except JANOValidationError as e:
        # Password or username doesn't meet JANO security policies
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": e.message,
                "violations": e.violations
            },
        )
        
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


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Update user information. Only ROOT users can perform this operation.",
    dependencies=[Depends(require_root_role)],
)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
) -> UserResponse:
    """
    Update user information.
    
    Protected endpoint - Requires ROOT role.
    
    Args:
        user_id: UUID of the user to update
        request: User update data
        
    Returns:
        UserResponse with updated user data
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 404: User not found
        HTTPException 409: Email already exists
        HTTPException 500: Internal server error
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update user endpoint not yet implemented"
    )


@router.patch(
    "/{user_id}/disable",
    status_code=status.HTTP_200_OK,
    summary="Disable user",
    description="Disable a user account. Only ROOT users can perform this operation.",
    dependencies=[Depends(require_root_role)],
)
async def disable_user(
    user_id: UUID,
) -> dict:
    """
    Disable user account.
    
    Protected endpoint - Requires ROOT role.
    Sets is_active=False for the user.
    
    Args:
        user_id: UUID of the user to disable
        
    Returns:
        Success message
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Disable user endpoint not yet implemented"
    )


@router.patch(
    "/{user_id}/enable",
    status_code=status.HTTP_200_OK,
    summary="Enable user",
    description="Enable a user account. Only ROOT users can perform this operation.",
    dependencies=[Depends(require_root_role)],
)
async def enable_user(
    user_id: UUID,
) -> dict:
    """
    Enable user account.
    
    Protected endpoint - Requires ROOT role.
    Sets is_active=True for the user.
    
    Args:
        user_id: UUID of the user to enable
        
    Returns:
        Success message
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Enable user endpoint not yet implemented"
    )

