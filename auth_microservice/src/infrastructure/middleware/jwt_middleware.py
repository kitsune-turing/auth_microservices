"""JWT Authentication Middleware.

Provides JWT validation for protected endpoints.
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.domain.value_objects import TokenPayload
from src.domain.exceptions import (
    MissingAuthHeaderException,
    TokenExpiredException,
    InvalidTokenException,
)
from src.application.use_cases import ValidateTokenUseCase
from src.infrastructure.adapters.services import JWTService

logger = logging.getLogger(__name__)

# Security scheme for Swagger UI
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    Dependency to get current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        TokenPayload with user information
        
    Raises:
        HTTPException 401: If token is invalid or expired
    """
    if not credentials:
        logger.warning("Missing authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Create JWT service and validate token use case
        jwt_service = JWTService()
        validate_use_case = ValidateTokenUseCase(jwt_service)
        
        # Validate token
        token_payload = await validate_use_case.execute(token)
        
        return token_payload
        
    except TokenExpiredException:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenException as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[TokenPayload]:
    """
    Dependency to get current user from JWT token (optional).
    
    Returns None if no token is provided instead of raising an exception.
    
    Args:
        credentials: HTTP Bearer credentials (optional)
        
    Returns:
        TokenPayload with user information or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to require specific roles.
    
    Args:
        allowed_roles: List of allowed role names
        
    Returns:
        Dependency function
        
    Example:
        @router.get("/admin-only", dependencies=[Depends(require_role(["ROOT"]))])
    """
    async def role_checker(
        current_user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        if current_user.role not in allowed_roles:
            logger.warning(f"User {current_user.username} does not have required role")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}",
            )
        return current_user
    
    return role_checker


def require_permission(required_permissions: list[str]):
    """
    Dependency factory to require specific permissions.
    
    Args:
        required_permissions: List of required permission names
        
    Returns:
        Dependency function
        
    Example:
        @router.post("/users", dependencies=[Depends(require_permission(["create_user"]))])
    """
    async def permission_checker(
        current_user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        if not all(perm in current_user.permissions for perm in required_permissions):
            logger.warning(f"User {current_user.username} lacks required permissions")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permissions}",
            )
        return current_user
    
    return permission_checker


__all__ = [
    "security",
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "require_permission",
]
