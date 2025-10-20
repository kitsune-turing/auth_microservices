"""Verify Login Use Case - Step 2: Validate OTP and generate tokens."""
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.domain.ports import JWTServicePort, UsersServicePort, OTPServicePort
from src.core.utils.security import sanitize_email_for_log, sanitize_username_for_log
from src.domain.exceptions import InvalidOTPException
from src.application.dtos import VerifyLoginRequest, LoginResponse

logger = logging.getLogger(__name__)


class VerifyLoginUseCase:
    """Use case for verifying OTP and completing login."""
    
    def __init__(
        self,
        jwt_service: JWTServicePort,
        users_service: UsersServicePort,
        otp_service: OTPServicePort,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        """Initialize verify login use case."""
        self.jwt_service = jwt_service
        self.users_service = users_service
        self.otp_service = otp_service
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    async def execute(
        self, 
        request: VerifyLoginRequest,
    ) -> LoginResponse:
        """
        Execute login verification with OTP.
        
        Args:
            request: Verify login request with otp_id and OTP code
            
        Returns:
            LoginResponse with tokens and user info
            
        Raises:
            InvalidOTPException: If OTP is invalid or expired
        """
        logger.info(f"Verifying OTP with otp_id: {request.otp_id}")
        
        # Step 1: Validate OTP and get user info from validation response
        otp_validation = await self.otp_service.validate_otp(
            otp_id=request.otp_id,
            otp_code=request.otp_code,
        )
        
        if not otp_validation or not otp_validation.get("valid"):
            logger.warning(f"Invalid OTP for otp_id: {request.otp_id}")
            raise InvalidOTPException("Invalid or expired OTP code")
        
        # Extract user_id and email from OTP validation response
        user_id = str(otp_validation.get("user_id"))
        email = otp_validation.get("email")
        
        logger.info(f"OTP validated successfully for user: {user_id}")
        
        # Step 2: Get complete user data
        user_data = await self.users_service.get_user_by_email(email)
        
        if not user_data:
            logger.warning(f"User not found for email: {sanitize_email_for_log(email)}")
            raise InvalidOTPException("User not found")
        
        # Step 3: Extract user information
        username = user_data["username"]
        role = user_data["role"]
        permissions = user_data.get("permissions", [])
        team_name = user_data.get("team_name")
        
        # Step 4: Generate access token
        access_token_str, _, _ = self.jwt_service.create_access_token(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions,
            team_name=team_name,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )
        
        # Step 5: Generate refresh token
        refresh_token_str, _, _ = self.jwt_service.create_refresh_token(
            user_id=user_id,
            username=username,
            expires_delta=timedelta(days=self.refresh_token_expire_days),
        )
        
        logger.info(f"Tokens generated for user: {sanitize_username_for_log(username)}")
        
        # NOTE: Skipping token and session storage for now due to schema mismatch
        # In production, tokens should be persisted with auth_tokens table
        
        # Step 6: Build response (without persisting tokens to DB for now)
        return LoginResponse(
            access_token=access_token_str,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user={
                "user_id": user_id,
                "username": username,
                "email": user_data.get("email"),
                "role": role,
                "permissions": permissions,
                "team_name": team_name,
            },
        )


__all__ = ["VerifyLoginUseCase"]
