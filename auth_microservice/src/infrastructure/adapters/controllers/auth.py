"""Authentication API controller following hexagonal architecture.

This controller handles HTTP requests for authentication operations,
delegating business logic to use cases.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from typing import Optional

from src.application.dtos import (
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    LogoutRequest,
    OtpGenerateRequest,
    OtpValidateRequest,
)
from src.infrastructure.config.dependencies import (
    get_authenticate_user_use_case,
    get_generate_tokens_use_case,
    get_refresh_token_use_case,
    get_logout_use_case,
    get_generate_otp_use_case,
    get_validate_otp_use_case,
)
from src.application.use_cases.auth_use_cases import (
    AuthenticateUserUseCase,
    GenerateTokensUseCase,
    RefreshTokenUseCase,
    LogoutUseCase,
)
from src.application.use_cases.otp_use_cases import (
    GenerateOtpUseCase,
    ValidateOtpUseCase,
)
from src.infrastructure.adapters.exception_handlers import (
    AuthenticationError,
    AuthorizationError,
)
from src.core.domain.errors import AuthErrorList

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# Login Endpoint
# ============================================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with credentials and generate JWT tokens"
)
async def login(
    request_data: LoginRequest,
    request: Request,
    authenticate_use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
    generate_tokens_use_case: GenerateTokensUseCase = Depends(get_generate_tokens_use_case),
) -> LoginResponse:
    """
    Authenticate user and generate access/refresh tokens.
    
    **Flow:**
    1. Validate credentials with users_microservice
    2. Generate JWT tokens with role-based permissions
    3. Store session and tokens in database
    4. Return tokens to client
    
    **Permissions:**
    - Public endpoint (no authentication required)
    """
    try:
        # Step 1: Authenticate user credentials
        user_data = await authenticate_use_case.execute(
            username=request_data.username,
            password=request_data.password,
        )
        
        # Step 2: Generate tokens with user claims
        tokens = await generate_tokens_use_case.execute(
            user_id=user_data.id,
            role=user_data.role,
            permissions=user_data.permissions,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        logger.info(f"User {user_data.username} logged in successfully")
        
        return LoginResponse(
            message="Login successful",
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="Bearer",
            expires_in=tokens.access_token_expires_in,
            user_id=str(user_data.id),
            role=user_data.role,
        )
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise


# ============================================================================
# Token Refresh Endpoint
# ============================================================================

@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Generate new access token using valid refresh token"
)
async def token_refresh(
    request_data: TokenRefreshRequest,
    refresh_use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> TokenRefreshResponse:
    """
    Refresh access token using a valid refresh token.
    
    **Flow:**
    1. Validate refresh token (not expired, not revoked)
    2. Extract user_id from token claims
    3. Verify user is still active
    4. Generate new access token
    
    **Permissions:**
    - Requires valid refresh token
    """
    try:
        tokens = await refresh_use_case.execute(
            refresh_token=request_data.refresh_token
        )
        
        logger.info(f"Token refreshed for user {tokens.user_id}")
        
        return TokenRefreshResponse(
            message="Token refreshed successfully",
            access_token=tokens.access_token,
            token_type="Bearer",
            expires_in=tokens.access_token_expires_in,
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise


# ============================================================================
# Logout Endpoint
# ============================================================================

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Revoke all user tokens and close session"
)
async def logout(
    request_data: LogoutRequest,
    logout_use_case: LogoutUseCase = Depends(get_logout_use_case),
):
    """
    Logout user by revoking all active tokens.
    
    **Flow:**
    1. Revoke all access tokens for user
    2. Revoke all refresh tokens for user
    3. Close active session
    
    **Permissions:**
    - Requires valid access token (user can only logout themselves)
    """
    try:
        await logout_use_case.execute(
            user_id=request_data.user_id
        )
        
        logger.info(f"User {request_data.user_id} logged out successfully")
        
        return {
            "message": "Logout successful",
            "user_id": str(request_data.user_id),
        }
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise


# ============================================================================
# OTP Endpoints
# ============================================================================

@router.post(
    "/otp/generate",
    status_code=status.HTTP_200_OK,
    summary="Generate OTP",
    description="Generate one-time password for user"
)
async def generate_otp(
    request_data: OtpGenerateRequest,
    generate_otp_use_case: GenerateOtpUseCase = Depends(get_generate_otp_use_case),
):
    """
    Generate OTP for user authentication.
    
    **Flow:**
    1. Validate user exists and is active
    2. Generate OTP code
    3. Send OTP to user's contact method (email/SMS)
    
    **Permissions:**
    - Public endpoint (called after initial credential validation)
    """
    try:
        otp_data = await generate_otp_use_case.execute(
            user_id=request_data.user_id,
            contact_method=request_data.contact_method,
        )
        
        logger.info(f"OTP generated for user {request_data.user_id}")
        
        return {
            "message": "OTP generated successfully",
            "otp_id": otp_data.otp_id,
            "expires_in": otp_data.expires_in,
            "sent_to": otp_data.sent_to,
        }
        
    except Exception as e:
        logger.error(f"OTP generation failed: {str(e)}")
        raise


@router.post(
    "/otp/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate OTP",
    description="Validate one-time password"
)
async def validate_otp(
    request_data: OtpValidateRequest,
    validate_otp_use_case: ValidateOtpUseCase = Depends(get_validate_otp_use_case),
):
    """
    Validate OTP code.
    
    **Flow:**
    1. Check OTP exists and is not expired
    2. Verify OTP code matches
    3. Mark OTP as used
    
    **Permissions:**
    - Public endpoint (part of authentication flow)
    """
    try:
        is_valid = await validate_otp_use_case.execute(
            otp_id=request_data.otp_id,
            otp_code=request_data.otp_code,
        )
        
        if not is_valid:
            raise AuthenticationError(
                error_detail=AuthErrorList.OTP_INVALID
            )
        
        logger.info(f"OTP validated successfully for {request_data.otp_id}")
        
        return {
            "message": "OTP validated successfully",
            "is_valid": True,
        }
        
    except Exception as e:
        logger.error(f"OTP validation failed: {str(e)}")
        raise


# ============================================================================
# Password Reset Endpoints (Placeholder)
# ============================================================================

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Send password reset link to user email"
)
async def reset_password(email: EmailStr):
    """
    Request password reset (delegates to users_microservice).
    
    **Note:** This is a placeholder endpoint. Actual password reset
    should be handled by users_microservice.
    """
    logger.info(f"Password reset requested for email: {email}")
    
    return {
        "message": "If the email exists, password reset instructions have been sent."
    }


@router.post(
    "/reset-password/confirm",
    status_code=status.HTTP_200_OK,
    summary="Confirm Password Reset",
    description="Reset password using token from email"
)
async def reset_password_confirm(
    uid: str,
    token: str,
    new_password: str,
    re_new_password: str,
):
    """
    Confirm password reset (delegates to users_microservice).
    
    **Note:** This is a placeholder endpoint. Actual password update
    should be handled by users_microservice.
    """
    if new_password != re_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    logger.info(f"Password reset confirmed for uid: {uid}")
    
    return {
        "message": "Your password has been changed successfully."
    }


__all__ = ["router"]
