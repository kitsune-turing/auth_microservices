"""JANO Client for Users Microservice.

HTTP client for communicating with JANO (Configuration Rules) microservice
to validate passwords and usernames against security policies.
"""
import logging
import httpx
import os
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JANOValidationError(Exception):
    """Raised when JANO validation fails."""
    def __init__(self, message: str, violations: list[str] = None):
        self.message = message
        self.violations = violations or []
        super().__init__(self.message)


class JANODisabledException(Exception):
    """Raised when JANO validation is disabled."""
    pass


class JANOClient:
    """Client for JANO microservice communication."""
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        application_id: str = "users_service",
        enabled: bool = True
    ):
        """
        Initialize JANO client.
        
        Args:
            base_url: Base URL of JANO microservice
            timeout: Request timeout in seconds
            application_id: Identifier for this application
            enabled: Whether JANO validation is enabled
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.application_id = application_id
        self.enabled = enabled
        self.client = httpx.AsyncClient(timeout=timeout)
        
        status = "ENABLED" if enabled else "DISABLED"
        logger.info(f"JANO client initialized: {base_url} (timeout={timeout}s, status={status})")
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def validate_password(
        self,
        password: str,
        username: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> tuple[bool, list[str]]:
        """
        Validate a password against JANO security policies.
        
        Args:
            password: Password to validate
            username: Optional username (for pattern checking)
            user_id: Optional user ID (for history checking)
            
        Returns:
            Tuple of (is_valid, violations_list)
            
        Raises:
            JANOValidationError: If validation fails
            JANODisabledException: If JANO validation is disabled
            httpx.HTTPError: If communication with JANO fails
        """
        # If JANO is disabled, allow all passwords
        if not self.enabled:
            logger.debug("JANO validation is disabled - allowing password")
            return True, []
        
        url = f"{self.base_url}/api/v1/policies/validate-password"
        
        payload = {
            "password": password,
            "application_id": self.application_id,
        }
        
        if username:
            payload["username"] = username
        if user_id:
            payload["user_id"] = user_id
        
        try:
            logger.debug(f"Validating password with JANO for user: {username or user_id}")
            
            response = await self.client.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                is_valid = data.get("valid", False)
                violations = data.get("violations", [])
                
                if is_valid:
                    logger.info(f"Password validation passed for user: {username or user_id}")
                    return True, []
                else:
                    logger.warning(
                        f"Password validation failed for user: {username or user_id}. "
                        f"Violations: {violations}"
                    )
                    return False, violations
            
            elif response.status_code == 400:
                # Bad request - validation failed
                data = response.json()
                violations = data.get("violations", [data.get("detail", "Unknown error")])
                logger.warning(f"Password validation failed: {violations}")
                return False, violations
            
            else:
                # Unexpected status code
                logger.error(
                    f"JANO password validation returned unexpected status: {response.status_code}"
                )
                response.raise_for_status()
                
        except httpx.TimeoutException:
            logger.error(f"JANO password validation timeout after {self.timeout}s")
            raise JANOValidationError(
                "Password validation service timeout. Please try again.",
                ["Service temporarily unavailable"]
            )
            
        except httpx.HTTPError as e:
            logger.error(f"JANO password validation HTTP error: {str(e)}")
            raise JANOValidationError(
                "Unable to validate password. Please try again.",
                ["Service communication error"]
            )
    
    async def validate_username(
        self,
        username: str,
    ) -> tuple[bool, list[str]]:
        """
        Validate a username against JANO security policies.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, violations_list)
            
        Raises:
            JANOValidationError: If validation fails
            JANODisabledException: If JANO validation is disabled
            httpx.HTTPError: If communication with JANO fails
        """
        # If JANO is disabled, allow all usernames
        if not self.enabled:
            logger.debug("JANO validation is disabled - allowing username")
            return True, []
        
        url = f"{self.base_url}/api/v1/policies/validate-username"
        
        payload = {
            "username": username,
            "application_id": self.application_id,
        }
        
        try:
            logger.debug(f"Validating username with JANO: {username}")
            
            response = await self.client.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                is_valid = data.get("valid", False)
                violations = data.get("violations", [])
                
                if is_valid:
                    logger.info(f"Username validation passed: {username}")
                    return True, []
                else:
                    logger.warning(
                        f"Username validation failed: {username}. "
                        f"Violations: {violations}"
                    )
                    return False, violations
            
            elif response.status_code == 400:
                # Bad request - validation failed
                data = response.json()
                violations = data.get("violations", [data.get("detail", "Unknown error")])
                logger.warning(f"Username validation failed: {violations}")
                return False, violations
            
            else:
                # Unexpected status code
                logger.error(
                    f"JANO username validation returned unexpected status: {response.status_code}"
                )
                response.raise_for_status()
                
        except httpx.TimeoutException:
            logger.error(f"JANO username validation timeout after {self.timeout}s")
            raise JANOValidationError(
                "Username validation service timeout. Please try again.",
                ["Service temporarily unavailable"]
            )
            
        except httpx.HTTPError as e:
            logger.error(f"JANO username validation HTTP error: {str(e)}")
            raise JANOValidationError(
                "Unable to validate username. Please try again.",
                ["Service communication error"]
            )
    
    async def health_check(self) -> bool:
        """
        Check if JANO service is available.
        
        Returns:
            True if JANO is healthy and enabled, False otherwise
        """
        # If JANO is disabled, consider it "healthy" (not needed)
        if not self.enabled:
            logger.debug("JANO validation is disabled - health check returns True")
            return True
        
        url = f"{self.base_url}/health"
        
        try:
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"JANO health check failed: {str(e)}")
            return False


# Global instance (initialized in main.py lifespan)
jano_client: Optional[JANOClient] = None


def get_jano_client() -> JANOClient:
    """
    Get the global JANO client instance.
    
    Returns:
        JANOClient instance
        
    Raises:
        RuntimeError: If JANO client is not initialized
    """
    if jano_client is None:
        raise RuntimeError(
            "JANO client not initialized. "
            "This should be done in the application lifespan."
        )
    return jano_client


__all__ = [
    "JANOClient",
    "JANOValidationError",
    "JANODisabledException",
    "jano_client",
    "get_jano_client",
]
