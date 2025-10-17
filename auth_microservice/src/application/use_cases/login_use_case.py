"""Login Use Case.

Handles user authentication by validating credentials and generating JWT tokens.
"""
import logging
from datetime import timedelta

from src.domain.ports import JWTServicePort, UsersServicePort
from src.domain.exceptions import InvalidCredentialsException, UsersServiceUnavailableException
from src.application.dtos import LoginRequest, LoginResponse

logger = logging.getLogger(__name__)


class LoginUseCase:
    """Use case for user login."""
    
    def __init__(
        self,
        jwt_service: JWTServicePort,
        users_service: UsersServicePort,
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7,
    ):
        """
        Initialize login use case.
        
        Args:
            jwt_service: JWT service implementation
            users_service: Users service client implementation
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self.jwt_service = jwt_service
        self.users_service = users_service
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    async def execute(self, request: LoginRequest) -> LoginResponse:
        """
        Execute login use case.
        
        Args:
            request: Login request with username and password
            
        Returns:
            LoginResponse with access token, refresh token, and user info
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
            UsersServiceUnavailableException: If users service is unavailable
        """
        logger.info(f"Login attempt for username: {request.username}")
        
        # Step 1: Validate credentials via users_microservice
        try:
            user_data = await self.users_service.validate_credentials(
                username=request.username,
                password=request.password,
            )
        except Exception as e:
            logger.error(f"Error validating credentials: {e}")
            raise
        
        # Step 2: Extract user information
        # If we reached here, credentials are valid (users_service would have raised InvalidCredentialsException otherwise)
        user_id = str(user_data["id"])
        username = user_data["username"]
        role = user_data["role"]
        permissions = user_data.get("permissions", [])
        team_name = user_data.get("team_name")
        
        logger.info(f"User {username} authenticated successfully. Role: {role}")
        
        # Step 3: Generate access token
        access_token = self.jwt_service.create_access_token(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions,
            team_name=team_name,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )
        
        # Step 5: Generate refresh token
        refresh_token = self.jwt_service.create_refresh_token(
            user_id=user_id,
            username=username,
            expires_delta=timedelta(days=self.refresh_token_expire_days),
        )
        
        logger.info(f"Tokens generated for user: {username}")
        
        # Step 6: Build response
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,  # Convert to seconds
            user={
                "user_id": user_id,
                "username": username,
                "email": user_data.get("email"),
                "role": role,
                "permissions": permissions,
                "team_name": team_name,
            },
        )


__all__ = ["LoginUseCase"]
