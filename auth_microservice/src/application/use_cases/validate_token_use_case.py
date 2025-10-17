"""Validate Token Use Case.

Handles JWT token validation and extraction of user information.
"""
import logging

from src.domain.ports import JWTServicePort
from src.domain.value_objects import TokenPayload
from src.domain.exceptions import (
    TokenExpiredException,
    InvalidTokenException,
)

logger = logging.getLogger(__name__)


class ValidateTokenUseCase:
    """Use case for validating JWT tokens."""
    
    def __init__(self, jwt_service: JWTServicePort):
        """
        Initialize validate token use case.
        
        Args:
            jwt_service: JWT service implementation
        """
        self.jwt_service = jwt_service
    
    async def execute(self, token: str) -> TokenPayload:
        """
        Execute token validation use case.
        
        Args:
            token: JWT token string to validate
            
        Returns:
            TokenPayload with decoded token data
            
        Raises:
            TokenExpiredException: If token is expired
            InvalidTokenException: If token is invalid
        """
        logger.debug("Validating JWT token")
        
        try:
            # Decode and validate token
            token_payload = self.jwt_service.decode_token(token)
            
            # Verify it's an access token
            if not token_payload.is_access_token():
                logger.warning("Token is not an access token")
                raise InvalidTokenException("Provided token is not an access token")
            
            logger.debug(f"Token validated successfully for user: {token_payload.username}")
            return token_payload
            
        except TokenExpiredException:
            logger.warning("Token has expired")
            raise
        except InvalidTokenException:
            logger.warning("Invalid token")
            raise


__all__ = ["ValidateTokenUseCase"]
