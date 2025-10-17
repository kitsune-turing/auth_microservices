"""OTP Service Port Interface.

Defines the contract for communication with otp_microservice (future implementation).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class OTPServicePort(ABC):
    """Port interface for otp_microservice communication."""
    
    @abstractmethod
    async def generate_otp(self, user_id: str, delivery_method: str = "email") -> Dict[str, Any]:
        """
        Generate OTP code for user.
        
        Args:
            user_id: User ID (UUID as string)
            delivery_method: Delivery method (email or sms)
            
        Returns:
            Dict with OTP data:
            {
                "otp_id": str,
                "expires_at": str (ISO format),
                "delivery_method": str,
                "otp_code": str (only in development)
            }
            
        Raises:
            OTPServiceUnavailableException: If service is unavailable
        """
        pass
    
    @abstractmethod
    async def validate_otp(
        self,
        user_id: str,
        otp_code: str,
    ) -> bool:
        """
        Validate OTP code for user.
        
        Args:
            user_id: User ID (UUID as string)
            otp_code: OTP code to validate
            
        Returns:
            True if OTP is valid, False otherwise
            
        Raises:
            OTPServiceUnavailableException: If service is unavailable
        """
        pass


__all__ = ["OTPServicePort"]
__all__ = ["OTPServicePort"]
