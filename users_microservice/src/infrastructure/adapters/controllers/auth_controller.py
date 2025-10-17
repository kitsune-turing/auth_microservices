"""Authentication Controller for Users Microservice.

This controller handles authentication-related endpoints that will be called
by the auth_microservice to validate user credentials.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos import (
    ValidateCredentialsRequest,
    ValidateCredentialsByEmailRequest,
    ValidateCredentialsResponse,
    UserResponse
)
from src.application.use_cases.validate_credentials_use_case import ValidateCredentialsUseCase
from src.application.use_cases.validate_credentials_by_email_use_case import ValidateCredentialsByEmailUseCase
from src.application.use_cases.get_user_by_email_use_case import GetUserByEmailUseCase
from src.infrastructure.config.dependencies import (
    get_validate_credentials_use_case,
    get_validate_credentials_by_email_use_case,
    get_user_by_email_use_case
)


router = APIRouter(
    prefix="/api/users",
    tags=["authentication"],
)


@router.post(
    "/validate-credentials",
    response_model=ValidateCredentialsResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate user credentials",
    description=(
        "Validates username and password. Used by auth_microservice "
        "during login process. Returns user data with role and permissions."
    ),
)
async def validate_credentials(
    request: ValidateCredentialsRequest,
    use_case: ValidateCredentialsUseCase = Depends(get_validate_credentials_use_case),
) -> ValidateCredentialsResponse:
    """
    Validate user credentials.
    
    This endpoint is called by the auth_microservice to validate
    username and password using BCrypt.
    
    Args:
        request: Contains username and password
        use_case: Injected ValidateCredentialsUseCase
        
    Returns:
        ValidateCredentialsResponse with user data and permissions
        
    Raises:
        HTTPException 401: Invalid credentials or inactive user
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(
            username=request.username,
            password=request.password
        )
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
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
    "/validate-credentials-email",
    response_model=ValidateCredentialsResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate user credentials by email",
    description=(
        "Validates email and password. Used by auth_microservice "
        "during email-based login process. Returns user data with role and permissions."
    ),
)
async def validate_credentials_by_email(
    request: ValidateCredentialsByEmailRequest,
    use_case: ValidateCredentialsByEmailUseCase = Depends(get_validate_credentials_by_email_use_case),
) -> ValidateCredentialsResponse:
    """
    Validate user credentials using email.
    
    This endpoint is called by the auth_microservice to validate
    email and password using BCrypt.
    
    Args:
        request: Contains email and password
        use_case: Injected ValidateCredentialsByEmailUseCase
        
    Returns:
        ValidateCredentialsResponse with user data and permissions
        
    Raises:
        HTTPException 401: Invalid credentials or inactive user
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(
            email=request.email,
            password=request.password
        )
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        return ValidateCredentialsResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/email/{email}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by email",
    description="Retrieves user information by email address. Used by auth_microservice.",
)
async def get_user_by_email(
    email: str,
    use_case: GetUserByEmailUseCase = Depends(get_user_by_email_use_case),
) -> UserResponse:
    """
    Get user by email address.
    
    This endpoint is called by the auth_microservice to retrieve
    user information by email.
    
    Args:
        email: User's email address
        use_case: Injected GetUserByEmailUseCase
        
    Returns:
        UserResponse with user data
        
    Raises:
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(email=email)
        return UserResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        # Check if it's a UserNotFoundException
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
