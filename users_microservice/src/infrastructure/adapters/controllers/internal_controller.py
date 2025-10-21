"""Internal Controller for Users Microservice.

Handles internal endpoints called ONLY by other microservices.
These endpoints are NOT protected by ROOT authorization since they are
for inter-service communication.

SECURITY NOTE: In production, these endpoints should be on a separate
internal network or protected by service-to-service authentication.
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
    prefix="/internal/users",
    tags=["internal"],
)


@router.post(
    "/validate-credentials",
    response_model=ValidateCredentialsResponse,
    status_code=status.HTTP_200_OK,
    summary="[INTERNAL] Validate user credentials",
    description=(
        "INTERNAL USE ONLY - Called by auth_microservice. "
        "Validates username and password. Returns user data with role and permissions."
    ),
)
async def validate_credentials(
    request: ValidateCredentialsRequest,
    use_case: ValidateCredentialsUseCase = Depends(get_validate_credentials_use_case),
) -> ValidateCredentialsResponse:
    """
    Validate user credentials (INTERNAL ENDPOINT).
    
    This endpoint is called ONLY by auth_microservice to validate
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
    summary="[INTERNAL] Validate user credentials by email",
    description=(
        "INTERNAL USE ONLY - Called by auth_microservice. "
        "Validates email and password. Returns user data with role and permissions."
    ),
)
async def validate_credentials_by_email(
    request: ValidateCredentialsByEmailRequest,
    use_case: ValidateCredentialsByEmailUseCase = Depends(get_validate_credentials_by_email_use_case),
) -> ValidateCredentialsResponse:
    """
    Validate user credentials using email (INTERNAL ENDPOINT).
    
    This endpoint is called ONLY by auth_microservice to validate
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/email/{email}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="[INTERNAL] Get user by email",
    description="INTERNAL USE ONLY - Retrieves user information by email address. Called by auth_microservice.",
)
async def get_user_by_email(
    email: str,
    use_case: GetUserByEmailUseCase = Depends(get_user_by_email_use_case),
) -> UserResponse:
    """
    Get user by email address (INTERNAL ENDPOINT).
    
    This endpoint is called ONLY by auth_microservice.
    
    Args:
        email: User email address
        use_case: Injected GetUserByEmailUseCase
        
    Returns:
        UserResponse with user data
        
    Raises:
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        result = await use_case.execute(email)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found with email: {email}",
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/test/db-schema",
    status_code=status.HTTP_200_OK,
    summary="[TEST] Verify database schema and ORM",
    description="TEST ENDPOINT - Verifies that SQLAlchemy models can connect to siata_auth schema correctly.",
)
async def test_db_schema() -> dict:
    """
    Test endpoint to verify database connection and schema mapping.
    
    This is a temporary endpoint to validate that the ORM correctly
    connects to siata_auth schema.
    
    Returns:
        Status information about the database connection
    """
    try:
        from src.infrastructure.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            # Test query to verify schema connection
            from sqlalchemy import text
            
            result = await session.execute(
                text("SELECT COUNT(*) as user_count FROM siata_auth.users")
            )
            count_row = result.fetchone()
            user_count = count_row[0] if count_row else 0
            
            return {
                "status": "✓ OK",
                "message": "Database connection and schema mapping verified",
                "schema": "siata_auth",
                "table": "users",
                "user_count": user_count
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "✗ ERROR",
                "error": str(e),
                "type": type(e).__name__
            }
        )
