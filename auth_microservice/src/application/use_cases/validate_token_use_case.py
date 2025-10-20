"""Validate Token Use Case.

Handles JWT token validation and extraction of user information.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID

from src.domain.ports import JWTServicePort
from src.core.ports.repository_ports import AuthTokenRepositoryPort
from src.domain.value_objects import TokenPayload
from src.domain.exceptions import (
    TokenExpiredException,
    InvalidTokenException,
)
from src.core.utils.security import hash_token, validate_jti_format

logger = logging.getLogger(__name__)


class ValidateTokenUseCase:
    """Use case for validating JWT tokens."""
    
    def __init__(
        self, 
        jwt_service: JWTServicePort,
        token_repository: AuthTokenRepositoryPort,
    ):
        """
        Initialize validate token use case.
        
        Args:
            jwt_service: JWT service implementation
            token_repository: Token repository for DB verification
        """
        self.jwt_service = jwt_service
        self.token_repository = token_repository
    
    async def execute(self, token: str) -> TokenPayload:
        """
        Execute token validation use case.
        
        Args:
            token: JWT token string to validate
            
        Returns:
            TokenPayload with decoded token data
            
        Raises:
            TokenExpiredException: If token is expired
            InvalidTokenException: If token is invalid or revoked
        """
        logger.debug("Validating JWT token")
        
        try:
            # Step 1: Decode and validate token signature
            token_payload = self.jwt_service.decode_token(token)
            
            # Step 2: Verify it's an access token
            if not token_payload.is_access_token():
                logger.warning("Token is not an access token")
                raise InvalidTokenException("Provided token is not an access token")
            
            # Step 3: Extract and validate jti (JWT ID)
            jti_str = token_payload.jti
            if not jti_str or not validate_jti_format(jti_str):
                logger.warning("Invalid or missing jti in token")
                raise InvalidTokenException("Token missing valid JWT ID")
            
            jti = UUID(jti_str)
            
            # Step 4: Verify token exists in database by jti
            token_entity = await self.token_repository.get_by_jti(jti)
            
            if not token_entity:
                logger.warning(f"Token with jti {jti} not found in database")
                raise InvalidTokenException("Token not found in database")
            
            # Step 5: Check if token has been revoked
            if token_entity.revoked:
                logger.warning(f"Token {jti} has been revoked")
                raise InvalidTokenException("Token has been revoked")
            
            # Step 6: Verify token has not expired in DB
            if token_entity.expires_at < datetime.now(timezone.utc):
                logger.warning(f"Token {jti} has expired in database")
                raise TokenExpiredException("Token has expired")
            
            # Step 7: Verify token hash matches (prevents token substitution)
            token_hash = hash_token(token)
            if token_entity.token_hash != token_hash:
                logger.error(f"Token hash mismatch for jti {jti}")
                raise InvalidTokenException("Token hash verification failed")
            
            logger.debug(f"Token validated successfully for user: {token_payload.username}")
            return token_payload
            
        except TokenExpiredException:
            logger.warning("Token has expired")
            raise
        except InvalidTokenException:
            logger.warning("Invalid token")
            raise


__all__ = ["ValidateTokenUseCase"]
