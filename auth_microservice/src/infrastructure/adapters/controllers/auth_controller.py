"""Auth Controller.

Handles authentication endpoints (login, refresh, logout, etc.).
"""
import logging
from fastapi import APIRouter, Depends, status, Request

from src.application.dtos import (
    LoginRequest,
    LoginInitResponse,
    VerifyLoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    CurrentUserResponse,
)
from pydantic import BaseModel
from src.application.use_cases import (
    LoginUseCase,
    LoginInitUseCase,
    VerifyLoginUseCase,
    RefreshTokenUseCase,
)
from src.domain.value_objects import TokenPayload
from src.infrastructure.middleware import get_current_user
from src.infrastructure.adapters.services import (
    JWTService,
    UsersServiceClient,
    OTPServiceClient,
    JANOServiceClient,
)
from src.infrastructure.dependencies import (
    get_token_repository,
    get_session_repository,
)
from src.core.ports.repository_ports import (
    AuthTokenRepositoryPort,
    SessionRepositoryPort,
)
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for X-Forwarded-For header (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    return request.client.host if request.client else "0.0.0.0"


def get_user_agent(request: Request) -> str:
    """
    Extract user agent from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User agent string
    """
    return request.headers.get("User-Agent", "Unknown")

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/login",
    response_model=LoginInitResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate login - Step 1",
    description=(
        "Authenticate user with email and password. "
        "Generates and sends OTP to user's email. "
        "User must verify OTP using /auth/verify-login endpoint."
    ),
)
async def login(
    request: LoginRequest,
    http_request: Request,
) -> LoginInitResponse:
    """
    Login initialization endpoint - Step 1.
    
    Validates credentials and sends OTP to user's email.
    
    Args:
        request: Login request with email and password
        http_request: FastAPI request for IP/user agent extraction
        
    Returns:
        LoginInitResponse with OTP sent confirmation
        
    Raises:
        401: Invalid credentials
        429: Rate limit exceeded
        503: Users or OTP service unavailable
    """
    logger.info(f"Login init request for email: {request.email}")
    
    # Extract client info for JANO validation
    ip_address = get_client_ip(http_request)
    user_agent = get_user_agent(http_request)
    
    # Create dependencies
    users_service = UsersServiceClient()
    otp_service = OTPServiceClient()
    jano_service = JANOServiceClient()
    
    # Create and execute use case
    use_case = LoginInitUseCase(
        users_service=users_service,
        otp_service=otp_service,
        jano_service=jano_service,
    )
    
    result = await use_case.execute(
        request=request,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    logger.info(f"OTP sent for email: {request.email}")
    return result


@router.post(
    "/verify-login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify login with OTP - Step 2",
    description=(
        "Verify OTP code and complete login process. "
        "Returns access token and refresh token upon successful verification."
    ),
)
async def verify_login(
    verify_request: VerifyLoginRequest,
    http_request: Request,
    token_repository: AuthTokenRepositoryPort = Depends(get_token_repository),
    session_repository: SessionRepositoryPort = Depends(get_session_repository),
) -> LoginResponse:
    """
    Verify login endpoint - Step 2.
    
    Validates OTP and generates JWT tokens.
    Saves tokens and session to database.
    
    Args:
        verify_request: Verify login request with email and OTP code
        http_request: HTTP request object for extracting client info
        token_repository: Token repository dependency
        session_repository: Session repository dependency
        
    Returns:
        LoginResponse with tokens and user information
        
    Raises:
        401: Invalid or expired OTP
        503: Services unavailable
    """
    logger.info(f"Verify login request for otp_id: {verify_request.otp_id}")
    
    # Create service dependencies
    jwt_service = JWTService()
    users_service = UsersServiceClient()
    otp_service = OTPServiceClient()
    
    # Create and execute use case
    use_case = VerifyLoginUseCase(
        jwt_service=jwt_service,
        users_service=users_service,
        otp_service=otp_service,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    )
    
    result = await use_case.execute(verify_request)
    
    logger.info(f"User logged in successfully for otp_id: {verify_request.otp_id}")
    return result


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    token_repository: AuthTokenRepositoryPort = Depends(get_token_repository),
) -> TokenResponse:
    """
    Refresh token endpoint.
    
    Generates a new access token from a valid refresh token.
    Saves new token to database.
    
    Args:
        request: Refresh token request
        token_repository: Token repository dependency
        
    Returns:
        TokenResponse with new access token
        
    Raises:
        401: Invalid or expired refresh token
    """
    logger.info("Refresh token request received")
    
    # Create service dependencies
    jwt_service = JWTService()
    users_service = UsersServiceClient()
    
    # Create and execute use case
    use_case = RefreshTokenUseCase(
        jwt_service=jwt_service,
        users_service=users_service,
        token_repository=token_repository,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    
    result = await use_case.execute(request)
    
    logger.info("New access token generated and saved")
    return result


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get information about the currently authenticated user.",
)
async def get_me(
    current_user: TokenPayload = Depends(get_current_user),
) -> CurrentUserResponse:
    """
    Get current user endpoint.
    
    Returns information about the authenticated user from the JWT token.
    
    Args:
        current_user: Current user from JWT token (injected)
        
    Returns:
        CurrentUserResponse with user information
    """
    logger.debug(f"Get current user for: {current_user.username}")
    
    # Get fresh user data
    users_service = UsersServiceClient()
    user_data = await users_service.get_user_by_id(current_user.sub)
    
    if user_data:
        return CurrentUserResponse(
            user_id=user_data.get("id") or current_user.sub,
            username=user_data.get("username") or current_user.username,
            email=user_data.get("email", ""),
            role=user_data.get("role") or current_user.role,
            permissions=user_data.get("permissions") or current_user.permissions,
            team_name=user_data.get("team_name") or current_user.team_name,
        )
    else:
        # Fallback to token data if user service is unavailable
        return CurrentUserResponse(
            user_id=current_user.sub,
            username=current_user.username,
            email="",
            role=current_user.role,
            permissions=current_user.permissions,
            team_name=current_user.team_name,
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout current user by revoking access token and ending active sessions.",
)
async def logout(
    http_request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    token_repository: AuthTokenRepositoryPort = Depends(get_token_repository),
    session_repository: SessionRepositoryPort = Depends(get_session_repository),
):
    """
    Logout endpoint.
    
    Revokes the current access token and ends associated sessions in the database.
    
    Args:
        http_request: HTTP request object to extract token
        current_user: Current user from JWT token (injected)
        token_repository: Token repository dependency
        session_repository: Session repository dependency
        
    Returns:
        Logout confirmation message
    """
    logger.info(f"Logout request for user: {current_user.username}")
    
    # Extract the access token from Authorization header
    authorization = http_request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        access_token_string = authorization[7:]  # Remove "Bearer " prefix
    else:
        access_token_string = ""
    
    # Import and create use case
    from src.application.use_cases import LogoutUseCase
    
    use_case = LogoutUseCase(
        token_repository=token_repository,
        session_repository=session_repository,
    )
    
    result = await use_case.execute(current_user, access_token_string)
    
    logger.info(f"User {current_user.username} logged out successfully")
    return result


class ValidateTokenRequest(BaseModel):
    """Request body for token validation."""
    token: str


@router.post(
    "/validate-token",
    status_code=status.HTTP_200_OK,
    summary="Validate Token",
    description="Validate a JWT token and return user information.",
)
async def validate_token(
    request: ValidateTokenRequest, 
    token_repository: AuthTokenRepositoryPort = Depends(get_token_repository)
):
    """
    Validate JWT token endpoint.
    
    Used by other microservices to validate tokens and get user info.
    
    Args:
        request: Token validation request with token string
        token_repository: Token repository dependency
        
    Returns:
        User information from token payload
        
    Raises:
        HTTPException 401: Invalid or expired token
    """
    logger.info("Token validation request received")
    
    jwt_service = JWTService()
    
    try:
        # Use ValidateTokenUseCase with jti verification
        from src.application.use_cases import ValidateTokenUseCase
        
        validate_use_case = ValidateTokenUseCase(
            jwt_service=jwt_service,
            token_repository=token_repository,
        )
        
        payload = await validate_use_case.execute(request.token)
        
        logger.info(f"Token validated successfully for user: {payload.sub}")
        
        # Return user info
        return {
            "user_id": payload.sub,
            "username": payload.username,
            "role": payload.role,
            "permissions": payload.permissions,
            "team_name": payload.team_name,
        }
        
    except Exception as e:
        logger.warning(f"Token validation failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


__all__ = ["router"]
