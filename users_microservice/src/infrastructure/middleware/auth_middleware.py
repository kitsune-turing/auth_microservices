"""Authentication and Authorization Middleware for Users Microservice.

Validates JWT tokens and enforces role-based access control.
"""
from fastapi import HTTPException, status, Header
from typing import Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Middleware for authentication and authorization."""
    
    def __init__(self, auth_service_url: str):
        """
        Initialize auth middleware.
        
        Args:
            auth_service_url: Base URL of auth microservice
        """
        self.auth_service_url = auth_service_url.rstrip('/')
        self.validate_url = f"{self.auth_service_url}/api/auth/validate-token"
    
    async def verify_token(self, authorization: str) -> dict:
        """
        Verify token with auth microservice.
        
        Args:
            authorization: Authorization header value (Bearer token)
            
        Returns:
            dict: Decoded token payload with user info
            
        Raises:
            HTTPException: If token is invalid or verification fails
        """
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.replace("Bearer ", "")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.validate_url,
                    json={"token": token},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Token validated for user: {data.get('user_id')}")
                    return data
                elif response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    logger.error(f"Auth service returned status {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Authentication service unavailable"
                    )
                    
        except httpx.RequestError as e:
            logger.error(f"Error connecting to auth service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
    
    async def require_root(
        self,
        authorization: Optional[str] = Header(None)
    ) -> dict:
        """
        Dependency that requires ROOT role.
        
        Args:
            authorization: Authorization header
            
        Returns:
            dict: User info from validated token
            
        Raises:
            HTTPException: If not authenticated or not ROOT role
        """
        user_data = await self.verify_token(authorization)
        
        role = user_data.get("role")
        if role != "root":
            logger.warning(
                f"Access denied for user {user_data.get('user_id')} with role {role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. ROOT role required."
            )
        
        logger.info(f"ROOT access granted for user {user_data.get('user_id')}")
        return user_data


# Global instance (will be initialized in main.py)
auth_middleware: Optional[AuthMiddleware] = None


def get_auth_middleware() -> AuthMiddleware:
    """Get global auth middleware instance."""
    if auth_middleware is None:
        raise RuntimeError("Auth middleware not initialized")
    return auth_middleware


async def require_root_role(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    FastAPI dependency that requires ROOT role.
    
    Usage:
        @router.post("/endpoint", dependencies=[Depends(require_root_role)])
        async def protected_endpoint():
            ...
    
    Returns:
        dict: User data from validated token
    """
    middleware = get_auth_middleware()
    return await middleware.require_root(authorization)
