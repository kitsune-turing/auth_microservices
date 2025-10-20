"""Refresh Token Use Case.

Handles token refresh by validating the refresh token and generating a new access token.
"""
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.domain.ports import JWTServicePort, UsersServicePort
from src.core.ports.repository_ports import AuthTokenRepositoryPort
from src.core.domain.entity import AuthToken, TokenType
from src.core.utils.security import hash_token, sanitize_username_for_log, validate_jti_format
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
        
        # Step 3: Verify refresh token exists in database and is not revoked
        refresh_jti = token_payload.jti
        if not refresh_jti or not validate_jti_format(refresh_jti):
            logger.warning("Invalid or missing jti in refresh token")
            raise InvalidRefreshTokenException("Refresh token missing valid JWT ID")
        
        refresh_token_entity = await self.token_repository.get_by_jti(UUID(refresh_jti))
        if not refresh_token_entity:
            logger.warning(f"Refresh token with jti {refresh_jti} not found in database")
            raise InvalidRefreshTokenException("Refresh token not found")
        
        if refresh_token_entity.revoked:
            logger.warning(f"Refresh token {refresh_jti} has been revoked")
            raise InvalidRefreshTokenException("Refresh token has been revoked")
        
        # Verify token hash matches
        refresh_token_hash = hash_token(request.refresh_token)
        if refresh_token_entity.token_hash != refresh_token_hash:
            logger.error(f"Refresh token hash mismatch for jti {refresh_jti}")
            raise InvalidRefreshTokenException("Refresh token verification failed")
        
        # Step 4: Get updated user information
        user_id = token_payload.sub
        username = token_payload.username
        
        try:
            user_data = await self.users_service.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error fetching user data: {e}")
            # If we can't fetch user data, use data from token
            user_data = None
        
        # Step 5: Use fresh data if available, otherwise use token data
        if user_data:
            role = user_data.get("role", token_payload.role)
            permissions = user_data.get("permissions", token_payload.permissions)
            team_name = user_data.get("team_name", token_payload.team_name)
        else:
            role = token_payload.role
            permissions = token_payload.permissions
            team_name = token_payload.team_name
        
        logger.info(f"Generating new access token for user: {sanitize_username_for_log(username)}")
        
        # Step 6: Generate new access token with ID
        access_token_str, access_token_id, _ = self.jwt_service.create_access_token(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions,
            team_name=team_name,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )
        
        logger.info(f"New access token generated for user: {sanitize_username_for_log(username)}")
        
        # Step 7: Save new access token to database (hash for security)
        access_token_hash = hash_token(access_token_str)
        access_token_entity = AuthToken(
            token_id=UUID(access_token_id),
            user_id=UUID(user_id),
            token_type=TokenType.ACCESS,
            token_hash=access_token_hash,
            jti=UUID(access_token_id),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes),
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
