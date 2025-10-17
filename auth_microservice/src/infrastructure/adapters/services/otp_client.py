"""OTP Service Client.

HTTP client for communication with otp_microservice (future implementation).
"""
import logging
from typing import Dict, Any

import httpx

from src.domain.ports import OTPServicePort
from src.domain.exceptions import OTPServiceUnavailableException
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class OTPServiceClient(OTPServicePort):
    """HTTP client for otp_microservice."""
    
    def __init__(self, base_url: str = None, timeout: float = 10.0):
        """
        Initialize OTP service client.
        
        Args:
            base_url: Base URL of otp_microservice
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.OTP_SERVICE_URL
        self.timeout = timeout
        logger.info(f"OTPServiceClient initialized with base_url: {self.base_url}")
    
    async def generate_otp(self, user_id: str, delivery_method: str = "email") -> Dict[str, Any]:
        """Generate OTP code for user via OTP microservice."""
        url = f"{self.base_url}/api/otp/generate"
        
        payload = {
            "user_id": user_id,
            "delivery_method": delivery_method,
        }
        
        logger.info(f"Generating OTP for user: {user_id} via {delivery_method}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 201:
                    data = response.json()
                    logger.info(f"OTP generated successfully for user: {user_id}")
                    return data
                else:
                    logger.error(f"Unexpected response from OTP service: {response.status_code}")
                    raise OTPServiceUnavailableException(
                        f"Unexpected response: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout connecting to OTP service")
            raise OTPServiceUnavailableException("Request timeout")
            
        except httpx.ConnectError:
            logger.error("Cannot connect to OTP service")
            raise OTPServiceUnavailableException("Connection refused")
            
        except Exception as e:
            logger.error(f"Error communicating with OTP service: {e}")
            raise OTPServiceUnavailableException(str(e))
    
    async def validate_otp(self, user_id: str, otp_code: str) -> bool:
        """Validate OTP code for user via OTP microservice."""
        url = f"{self.base_url}/api/otp/validate"
        
        payload = {
            "user_id": user_id,
            "otp_code": otp_code,
        }
        
        logger.info(f"Validating OTP for user: {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get("is_valid", False)
                    logger.info(f"OTP validation result for user {user_id}: {is_valid}")
                    return is_valid
                else:
                    logger.warning(f"OTP validation failed with status: {response.status_code}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error("Timeout connecting to OTP service")
            raise OTPServiceUnavailableException("Request timeout")
            
        except httpx.ConnectError:
            logger.error("Cannot connect to OTP service")
            raise OTPServiceUnavailableException("Connection refused")
            
        except Exception as e:
            logger.error(f"Error communicating with OTP service: {e}")
            raise OTPServiceUnavailableException(str(e))


__all__ = ["OTPServiceClient"]
