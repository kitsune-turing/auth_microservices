"""Refresh Token Use Case.

Handles token refresh by validating the refresh token and generating a new access token.
"""
import logging
from datetime import timedelta, timezone
from uuid import UUID

from src.domain.ports import JWTServicePort, UsersServicePort
from src.core.ports.repository_ports import AuthTokenRepositoryPort
from src.core.domain.entity import AuthToken, TokenType
from src.domain.exceptions import (
    InvalidRefreshTokenException,
    TokenExpiredException,
    InvalidTokenException,
)
from src.application.dtos import RefreshTokenRequest, TokenResponse

logger = logging.getLogger(__name__)


class RefreshTokenUseCase:
    """Use case for refreshing access tokens."""
    
    def __init__(
        self,
        jwt_service: JWTServicePort,
        users_service: UsersServicePort,
        token_repository: AuthTokenRepositoryPort,
        access_token_expire_minutes: int = 60,
    ):
        """
        Initialize refresh token use case.
        
        Args:
            jwt_service: JWT service implementation
            users_service: Users service client implementation
            token_repository: Token repository for storing tokens
            access_token_expire_minutes: Access token expiration in minutes
        """
        self.jwt_service = jwt_service
        self.users_service = users_service
        self.token_repository = token_repository
        self.access_token_expire_minutes = access_token_expire_minutes
    
    async def execute(self, request: RefreshTokenRequest) -> TokenResponse:
        """
        Execute refresh token use case.
        
        Args:
            request: Refresh token request
            
        Returns:
            TokenResponse with new access token
            
        Raises:
            InvalidRefreshTokenException: If refresh token is invalid
            TokenExpiredException: If refresh token is expired
        """
        logger.info("Refresh token request received")
        
        # Step 1: Decode and validate refresh token
        try:
            token_payload = self.jwt_service.decode_token(request.refresh_token)
        except TokenExpiredException:
            logger.warning("Refresh token has expired")
            raise
        except InvalidTokenException:
            logger.warning("Invalid refresh token")
            raise InvalidRefreshTokenException()
        
        # Step 2: Verify it's a refresh token
        if not token_payload.is_refresh_token():
            logger.warning("Token is not a refresh token")
            raise InvalidRefreshTokenException("Provided token is not a refresh token")
        
        # Step 3: Get updated user information
        user_id = token_payload.sub
        username = token_payload.username
        
        try:
            user_data = await self.users_service.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error fetching user data: {e}")
            # If we can't fetch user data, use data from token
            user_data = None
        
        # Step 4: Use fresh data if available, otherwise use token data
        if user_data:
            role = user_data.get("role", token_payload.role)
            permissions = user_data.get("permissions", token_payload.permissions)
            team_name = user_data.get("team_name", token_payload.team_name)
        else:
            role = token_payload.role
            permissions = token_payload.permissions
            team_name = token_payload.team_name
        
        logger.info(f"Generating new access token for user: {username}")
        
        # Step 5: Generate new access token with ID
        access_token_str, access_token_id, access_expires_at = self.jwt_service.create_access_token(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions,
            team_name=team_name,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )
        
        logger.info(f"New access token generated for user: {username}")
        
        # Step 6: Save new access token to database
        access_token_entity = AuthToken(
            token_id=UUID(access_token_id),
            user_id=UUID(user_id),
            token_type=TokenType.ACCESS,
            token_string=access_token_str,
            expires_at=access_expires_at.replace(tzinfo=timezone.utc),
        )
        await self.token_repository.save(access_token_entity)
        logger.info(f"New access token saved to database: {access_token_id}")
        
        # Step 7: Return new token
        return TokenResponse(
            access_token=access_token_str,
            refresh_token=request.refresh_token,  # Return same refresh token
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
        )


__all__ = ["RefreshTokenUseCase"]
