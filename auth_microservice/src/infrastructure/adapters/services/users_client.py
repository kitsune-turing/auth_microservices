"""Users Service Client.

HTTP client for communication with users_microservice.
"""
import logging
from typing import Dict, Any, Optional

import httpx

from src.domain.ports import UsersServicePort
from src.domain.exceptions import (
    UsersServiceUnavailableException,
    InvalidCredentialsException,
)
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class UsersServiceClient(UsersServicePort):
    """HTTP client for users_microservice."""
    
    def __init__(self, base_url: str = None, timeout: float = 10.0):
        """
        Initialize users service client.
        
        Args:
            base_url: Base URL of users_microservice
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.USERS_SERVICE_URL
        self.timeout = timeout
        logger.info(f"UsersServiceClient initialized with base_url: {self.base_url}")
    
    async def validate_credentials(
        self,
        username: str,
        password: str,
    ) -> Dict[str, Any]:
        """Validate user credentials via users_microservice."""
        url = f"{self.base_url}/api/users/validate-credentials"
        
        payload = {
            "username": username,
            "password": password,
        }
        
        logger.info(f"Validating credentials for user: {username}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Credentials validated successfully for user: {username}")
                    return data
                    
                elif response.status_code == 401:
                    logger.warning(f"Invalid credentials for user: {username}")
                    raise InvalidCredentialsException()
                    
                else:
                    logger.error(f"Unexpected response from users service: {response.status_code}")
                    raise UsersServiceUnavailableException(
                        f"Unexpected response: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout connecting to users service")
            raise UsersServiceUnavailableException("Request timeout")
            
        except httpx.ConnectError:
            logger.error("Cannot connect to users service")
            raise UsersServiceUnavailableException("Connection refused")
            
        except InvalidCredentialsException:
            raise
            
        except Exception as e:
            logger.error(f"Error communicating with users service: {e}")
            raise UsersServiceUnavailableException(str(e))
    
    async def validate_credentials_by_email(
        self,
        email: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        """Validate user credentials by email via users_microservice."""
        url = f"{self.base_url}/api/users/validate-credentials-email"
        
        payload = {
            "email": email,
            "password": password,
        }
        
        logger.info(f"Validating credentials for email: {email}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Credentials validated successfully for email: {email}")
                    return data
                    
                elif response.status_code == 401:
                    logger.warning(f"Invalid credentials for email: {email}")
                    return None
                    
                else:
                    logger.error(f"Unexpected response from users service: {response.status_code}")
                    raise UsersServiceUnavailableException(
                        f"Unexpected response: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout connecting to users service")
            raise UsersServiceUnavailableException("Request timeout")
            
        except httpx.ConnectError:
            logger.error("Cannot connect to users service")
            raise UsersServiceUnavailableException("Connection refused")
            
        except Exception as e:
            logger.error(f"Error communicating with users service: {e}")
            raise UsersServiceUnavailableException(str(e))
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by ID."""
        url = f"{self.base_url}/api/users/{user_id}"
        
        logger.debug(f"Fetching user data for user_id: {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"User data fetched successfully for user_id: {user_id}")
                    return data
                    
                elif response.status_code == 404:
                    logger.warning(f"User not found: {user_id}")
                    return None
                    
                else:
                    logger.error(f"Unexpected response from users service: {response.status_code}")
                    raise UsersServiceUnavailableException(
                        f"Unexpected response: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout connecting to users service")
            raise UsersServiceUnavailableException("Request timeout")
            
        except httpx.ConnectError:
            logger.error("Cannot connect to users service")
            raise UsersServiceUnavailableException("Connection refused")
            
        except Exception as e:
            logger.error(f"Error communicating with users service: {e}")
            raise UsersServiceUnavailableException(str(e))
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user information by email."""
        url = f"{self.base_url}/api/users/email/{email}"
        
        logger.debug(f"Fetching user data for email: {email}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"User data fetched successfully for email: {email}")
                    return data
                    
                elif response.status_code == 404:
                    logger.warning(f"User not found: {email}")
                    return None
                    
                else:
                    logger.error(f"Unexpected response from users service: {response.status_code}")
                    raise UsersServiceUnavailableException(
                        f"Unexpected response: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout connecting to users service")
            raise UsersServiceUnavailableException("Request timeout")
            
        except httpx.ConnectError:
            logger.error("Cannot connect to users service")
            raise UsersServiceUnavailableException("Connection refused")
            
        except Exception as e:
            logger.error(f"Error communicating with users service: {e}")
            raise UsersServiceUnavailableException(str(e))


__all__ = ["UsersServiceClient"]
