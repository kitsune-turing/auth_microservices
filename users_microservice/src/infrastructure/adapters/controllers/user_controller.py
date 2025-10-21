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
from src.application.use_cases.update_user_use_case import UpdateUserUseCase
from src.application.use_cases.get_users_use_case import GetUsersUseCase
from src.application.use_cases.disable_user_use_case import DisableUserUseCase
from src.application.use_cases.enable_user_use_case import EnableUserUseCase
from src.infrastructure.config.dependencies import (
    get_get_user_use_case,
    get_create_user_use_case,
    get_update_user_use_case,
    get_get_users_use_case,
    get_disable_user_use_case,
    get_enable_user_use_case,
)
from src.infrastructure.middleware import require_root_role
from src.infrastructure.adapters.jano_client import JANOValidationError


router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="List all users with pagination. Requires ROOT role.",
    dependencies=[Depends(require_root_role)],
)
async def list_users(
    page: int = 1,
    size: int = 10,
    role: str = None,
    active_only: bool = False,
    use_case: GetUsersUseCase = Depends(get_get_users_use_case),
) -> dict:
    """
    List all users with pagination.
    
    Protected endpoint - Requires ROOT role.
    
    Args:
        page: Page number (starting from 1)
        size: Number of items per page
        role: Optional role filter
        active_only: If True, only return active users
        use_case: Injected GetUsersUseCase
        
    Returns:
        Dictionary with paginated users list
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(page=page, size=size, role=role, active_only=active_only)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
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
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case),
) -> UserResponse:
    """
    Update user information.
    
    Protected endpoint - Requires ROOT role.
    
    Args:
        user_id: UUID of the user to update
        request: User update data
        use_case: Injected UpdateUserUseCase
        
    Returns:
        UserResponse with updated user data
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 404: User not found
        HTTPException 409: Email already exists
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(user_id, request)
        return result
        
    except ValueError as e:
        error_msg = str(e)
        if "already in use" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
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
    use_case: DisableUserUseCase = Depends(get_disable_user_use_case),
) -> dict:
    """
    Disable user account.
    
    Protected endpoint - Requires ROOT role.
    Sets status='inactive' for the user.
    
    Args:
        user_id: UUID of the user to disable
        use_case: Injected DisableUserUseCase
        
    Returns:
        Success message
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(user_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
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
    use_case: EnableUserUseCase = Depends(get_enable_user_use_case),
) -> dict:
    """
    Enable user account.
    
    Protected endpoint - Requires ROOT role.
    Sets status='active' for the user.
    
    Args:
        user_id: UUID of the user to enable
        use_case: Injected EnableUserUseCase
        
    Returns:
        Success message
        
    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (not ROOT role)
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(user_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

