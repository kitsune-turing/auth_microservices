"""JANO Security Service Client.

Client for communicating with JANO (configuration_rules_microservice)
for security validation and policy enforcement.
"""
import logging
from typing import Optional, Dict, Any

import httpx

from src.domain.ports import JANOServicePort
from src.domain.exceptions import JANOServiceUnavailableException
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class JANOServiceClient(JANOServicePort):
    """Implementation of JANO service port using HTTP client."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize JANO service client.
        
        Args:
            base_url: Base URL of JANO microservice (default from settings)
            timeout: Request timeout in seconds (default from settings)
        """
        self.base_url = (base_url or settings.JANO_SERVICE_URL).rstrip("/")
        self.timeout = timeout or settings.JANO_SERVICE_TIMEOUT
    
    async def validate_password(self, password: str) -> Dict[str, Any]:
        """
        Validate password against JANO password policies.
        
        Args:
            password: Password to validate
            
        Returns:
            Validation result with is_valid, violations, warnings
            
        Raises:
            JANOServiceUnavailableException: If JANO service is unavailable
        """
        url = f"{self.base_url}/api/validate/password"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json={"password": password},
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Password validation result: {data}")
                    return data
                else:
                    logger.error(f"JANO password validation failed: {response.status_code}")
                    raise JANOServiceUnavailableException(
                        f"JANO returned status {response.status_code}"
                    )
        except httpx.TimeoutException:
            logger.error("JANO service timeout during password validation")
            raise JANOServiceUnavailableException("JANO service timeout")
        except httpx.ConnectError:
            logger.error("Cannot connect to JANO service")
            raise JANOServiceUnavailableException("Cannot connect to JANO service")
        except Exception as e:
            logger.error(f"Error validating password with JANO: {e}")
            raise JANOServiceUnavailableException(f"JANO error: {str(e)}")
    
    async def validate_request(
        self,
        user_id: str,
        role: str,
        endpoint: str,
        method: str,
        ip_address: str,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate request against JANO security rules.
        
        Args:
            user_id: User ID making the request
            role: User role
            endpoint: Endpoint being accessed
            method: HTTP method
            ip_address: Client IP address
            user_agent: User agent string
            
        Returns:
            Validation result with should_block, violations, warnings
            
        Raises:
            JANOServiceUnavailableException: If JANO service is unavailable
        """
        url = f"{self.base_url}/api/validate/request"
        
        payload = {
            "user_id": user_id,
            "role": role,
            "endpoint": endpoint,
            "method": method,
            "ip_address": ip_address,
        }
        
        if user_agent:
            payload["user_agent"] = user_agent
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Request validation result for user {user_id}: {data}")
                    return data
                else:
                    logger.error(f"JANO request validation failed: {response.status_code}")
                    raise JANOServiceUnavailableException(
                        f"JANO returned status {response.status_code}"
                    )
        except httpx.TimeoutException:
            logger.error("JANO service timeout during request validation")
            raise JANOServiceUnavailableException("JANO service timeout")
        except httpx.ConnectError:
            logger.error("Cannot connect to JANO service")
            raise JANOServiceUnavailableException("Cannot connect to JANO service")
        except Exception as e:
            logger.error(f"Error validating request with JANO: {e}")
            raise JANOServiceUnavailableException(f"JANO error: {str(e)}")
    
    async def validate_session(
        self,
        user_id: str,
        role: str,
        session_created_at: str,
        last_activity_at: str,
    ) -> Dict[str, Any]:
        """
        Validate session against JANO session policies.
        
        Args:
            user_id: User ID
            role: User role
            session_created_at: When session was created (ISO format)
            last_activity_at: Last activity timestamp (ISO format)
            
        Returns:
            Validation result with is_valid, violations
            
        Raises:
            JANOServiceUnavailableException: If JANO service is unavailable
        """
        url = f"{self.base_url}/api/validate/session"
        
        payload = {
            "user_id": user_id,
            "role": role,
            "session_created_at": session_created_at,
            "last_activity_at": last_activity_at,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Session validation result for user {user_id}: {data}")
                    return data
                else:
                    logger.error(f"JANO session validation failed: {response.status_code}")
                    raise JANOServiceUnavailableException(
                        f"JANO returned status {response.status_code}"
                    )
        except httpx.TimeoutException:
            logger.error("JANO service timeout during session validation")
            raise JANOServiceUnavailableException("JANO service timeout")
        except httpx.ConnectError:
            logger.error("Cannot connect to JANO service")
            raise JANOServiceUnavailableException("Cannot connect to JANO service")
        except Exception as e:
            logger.error(f"Error validating session with JANO: {e}")
            raise JANOServiceUnavailableException(f"JANO error: {str(e)}")
    
    async def validate_mfa_requirement(
        self,
        user_id: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Check if MFA is required for user.
        
        Args:
            user_id: User ID
            role: User role
            
        Returns:
            Validation result with mfa_required boolean
            
        Raises:
            JANOServiceUnavailableException: If JANO service is unavailable
        """
        url = f"{self.base_url}/api/validate/mfa"
        
        payload = {
            "user_id": user_id,
            "role": role,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"MFA validation result for user {user_id}: {data}")
                    return data
                else:
                    logger.error(f"JANO MFA validation failed: {response.status_code}")
                    raise JANOServiceUnavailableException(
                        f"JANO returned status {response.status_code}"
                    )
        except httpx.TimeoutException:
            logger.error("JANO service timeout during MFA validation")
            raise JANOServiceUnavailableException("JANO service timeout")
        except httpx.ConnectError:
            logger.error("Cannot connect to JANO service")
            raise JANOServiceUnavailableException("Cannot connect to JANO service")
        except Exception as e:
            logger.error(f"Error validating MFA with JANO: {e}")
            raise JANOServiceUnavailableException(f"JANO error: {str(e)}")


__all__ = ["JANOServiceClient"]
