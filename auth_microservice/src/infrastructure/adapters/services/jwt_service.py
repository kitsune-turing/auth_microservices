"""JWT Service Implementation.

Implements JWT token generation and validation using python-jose.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from jose import jwt, JWTError

from src.domain.ports import JWTServicePort
from src.domain.value_objects import TokenPayload
from src.domain.exceptions import (
    TokenExpiredException,
    InvalidTokenException,
)
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class JWTService(JWTServicePort):
    """JWT service implementation using python-jose."""
    
    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = None,
    ):
        """
        Initialize JWT service.
        
        Args:
            secret_key: Secret key for signing tokens (from settings if not provided)
            algorithm: Algorithm for signing (from settings if not provided)
        """
        self.secret_key = secret_key or settings.JWT_SECRET_KEY
        self.algorithm = algorithm or settings.JWT_ALGORITHM
        
        if len(self.secret_key) < 32:
            logger.warning("JWT secret key should be at least 32 characters long")
    
    def create_access_token(
        self,
        user_id: str,
        username: str,
        role: str,
        permissions: list[str],
        team_name: str | None = None,
        expires_delta: timedelta | None = None,
        token_id: str | None = None,
    ) -> tuple[str, str, datetime]:
        """
        Create a new access token.
        
        Returns:
            Tuple of (token_string, token_id, expires_at)
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        now = datetime.utcnow()
        expire = now + expires_delta
        
        # Generate unique token ID
        jti = token_id or str(uuid4())
        
        payload = {
            "jti": jti,
            "sub": user_id,
            "username": username,
            "role": role,
            "permissions": permissions,
            "team_name": team_name,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "token_type": "access",
        }
        
        try:
            encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Access token created for user: {username}, token_id: {jti}")
            return encoded_jwt, jti, expire
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
    
    def create_refresh_token(
        self,
        user_id: str,
        username: str,
        expires_delta: timedelta | None = None,
        token_id: str | None = None,
    ) -> tuple[str, str, datetime]:
        """
        Create a new refresh token.
        
        Returns:
            Tuple of (token_string, token_id, expires_at)
        """
        if expires_delta is None:
            expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        now = datetime.utcnow()
        expire = now + expires_delta
        
        # Generate unique token ID
        jti = token_id or str(uuid4())
        
        payload = {
            "jti": jti,
            "sub": user_id,
            "username": username,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "token_type": "refresh",
        }
        
        try:
            encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Refresh token created for user: {username}, token_id: {jti}")
            return encoded_jwt, jti, expire
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise
    
    def decode_token(self, token: str) -> TokenPayload:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                raise TokenExpiredException()
            
            # Create TokenPayload
            # For refresh tokens, set default values for missing fields
            token_type = payload.get("token_type", "access")
            
            if token_type == "refresh":
                # Refresh token has minimal fields
                token_payload = TokenPayload(
                    sub=payload["sub"],
                    username=payload["username"],
                    role="",  # Not included in refresh token
                    permissions=[],  # Not included in refresh token
                    team_name=None,
                    iat=payload["iat"],
                    exp=payload["exp"],
                    token_type=token_type,
                )
            else:
                # Access token has all fields
                token_payload = TokenPayload(
                    sub=payload["sub"],
                    username=payload["username"],
                    role=payload.get("role", ""),
                    permissions=payload.get("permissions", []),
                    team_name=payload.get("team_name"),
                    iat=payload["iat"],
                    exp=payload["exp"],
                    token_type=token_type,
                )
            
            return token_payload
            
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            raise InvalidTokenException(str(e))
        except TokenExpiredException:
            raise
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            raise InvalidTokenException(str(e))
    
    def verify_token(self, token: str) -> bool:
        """Verify if a token is valid."""
        try:
            self.decode_token(token)
            return True
        except (TokenExpiredException, InvalidTokenException):
            return False


__all__ = ["JWTService"]
