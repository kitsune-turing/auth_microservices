"""Verify Login Use Case - Step 2: Validate OTP and generate tokens."""
import logging
from datetime import timedelta, timezone
from uuid import UUID

from src.domain.ports import JWTServicePort, UsersServicePort, OTPServicePort
from src.core.ports.repository_ports import AuthTokenRepositoryPort, SessionRepositoryPort
from src.core.domain.entity import AuthToken, TokenType, Session
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
        token_repository: AuthTokenRepositoryPort,
        session_repository: SessionRepositoryPort,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        """Initialize verify login use case."""
        self.jwt_service = jwt_service
        self.users_service = users_service
        self.otp_service = otp_service
        self.token_repository = token_repository
        self.session_repository = session_repository
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    async def execute(
        self, 
        request: VerifyLoginRequest,
        ip_address: str = "0.0.0.0",
        user_agent: str = "Unknown"
    ) -> LoginResponse:
        """
        Execute login verification with OTP.
        
        Args:
            request: Verify login request with email and OTP code
            
        Returns:
            LoginResponse with tokens and user info
            
        Raises:
            InvalidOTPException: If OTP is invalid or expired
        """
        logger.info(f"Verifying OTP for email: {request.email}")
        
        # Step 1: Get user by email
        user_data = await self.users_service.get_user_by_email(request.email)
        
        if not user_data:
            logger.warning(f"User not found for email: {request.email}")
            raise InvalidOTPException("Invalid OTP or email")
        
        user_id = str(user_data["id"])
        
        # Step 2: Validate OTP
        otp_valid = await self.otp_service.validate_otp(
            user_id=user_id,
            otp_code=request.otp_code,
        )
        
        if not otp_valid:
            logger.warning(f"Invalid OTP for user: {user_id}")
            raise InvalidOTPException("Invalid or expired OTP code")
        
        logger.info(f"OTP validated successfully for user: {user_id}")
        
        # Step 3: Extract user information
        username = user_data["username"]
        role = user_data["role"]
        permissions = user_data.get("permissions", [])
        team_name = user_data.get("team_name")
        user_uuid = UUID(user_id)
        
        # Step 4: Generate access token with ID
        access_token_str, access_token_id, access_expires_at = self.jwt_service.create_access_token(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions,
            team_name=team_name,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )
        
        # Step 5: Generate refresh token with ID
        refresh_token_str, refresh_token_id, refresh_expires_at = self.jwt_service.create_refresh_token(
            user_id=user_id,
            username=username,
            expires_delta=timedelta(days=self.refresh_token_expire_days),
        )
        
        logger.info(f"Tokens generated for user: {username}")
        
        # Step 6: Save access token to database
        access_token_entity = AuthToken(
            token_id=UUID(access_token_id),
            user_id=user_uuid,
            token_type=TokenType.ACCESS,
            token_string=access_token_str,
            expires_at=access_expires_at.replace(tzinfo=timezone.utc),
        )
        await self.token_repository.save(access_token_entity)
        logger.info(f"Access token saved to database: {access_token_id}")
        
        # Step 7: Save refresh token to database
        refresh_token_entity = AuthToken(
            token_id=UUID(refresh_token_id),
            user_id=user_uuid,
            token_type=TokenType.REFRESH,
            token_string=refresh_token_str,
            expires_at=refresh_expires_at.replace(tzinfo=timezone.utc),
        )
        await self.token_repository.save(refresh_token_entity)
        logger.info(f"Refresh token saved to database: {refresh_token_id}")
        
        # Step 8: Create and save session
        session = Session(
            user_id=user_uuid,
            access_token_id=UUID(access_token_id),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=access_expires_at.replace(tzinfo=timezone.utc),
        )
        await self.session_repository.save(session)
        logger.info(f"Session created for user: {username}, session_id: {session.id}")
        
        # Step 9: Build response
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
