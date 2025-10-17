"""Generate OTP Use Case."""
import logging
import secrets
from datetime import datetime, UTC

from src.core.domain.entity import OTP, DeliveryMethod
from src.core.domain.exceptions import (
    OTPGenerationFailedException,
    InvalidDeliveryMethodException,
    NoContactMethodException,
)
from src.application.dtos import GenerateOTPRequest, GenerateOTPResponse

logger = logging.getLogger(__name__)


class GenerateOTPUseCase:
    """Use case for generating OTP."""
    
    def __init__(self):
        """Initialize use case."""
        # In a real implementation, inject OTP repository and notification service
        self.otp_storage: dict[str, OTP] = {}  # Mock storage
    
    def _generate_otp_code(self) -> str:
        """
        Generate a random 6-digit OTP code.
        
        Returns:
            6-digit OTP code as string
        """
        return f"{secrets.randbelow(1000000):06d}"
    
    def _get_recipient(self, user_id: str, delivery_method: str) -> str:
        """
        Get recipient contact information.
        
        In a real implementation, this would fetch from users_microservice.
        
        Args:
            user_id: User identifier
            delivery_method: email or sms
            
        Returns:
            Email address or phone number
        """
        # Mock implementation
        if delivery_method == "email":
            return f"user_{user_id}@example.com"
        else:  # sms
            return "+573001234567"
    
    def _mask_recipient(self, recipient: str, method: str) -> str:
        """
        Mask recipient for privacy.
        
        Args:
            recipient: Email or phone
            method: Delivery method
            
        Returns:
            Masked recipient
        """
        if method == "email":
            parts = recipient.split("@")
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                masked_username = username[0] + "*" * (len(username) - 2) + username[-1] if len(username) > 2 else username
                return f"{masked_username}@{domain}"
        else:  # phone
            if len(recipient) > 4:
                return recipient[:3] + "*" * (len(recipient) - 6) + recipient[-3:]
        return recipient
    
    async def execute(self, request: GenerateOTPRequest) -> GenerateOTPResponse:
        """
        Generate OTP for user.
        
        Args:
            request: OTP generation request
            
        Returns:
            GenerateOTPResponse with OTP details
            
        Raises:
            InvalidDeliveryMethodException: If delivery method is invalid
            OTPGenerationFailedException: If OTP generation fails
        """
        logger.info(f"Generating OTP for user {request.user_id} via {request.delivery_method}")
        
        # Validate delivery method
        if request.delivery_method not in ["email", "sms"]:
            raise InvalidDeliveryMethodException(request.delivery_method)
        
        try:
            # Generate OTP code
            otp_code = self._generate_otp_code()
            
            # Get recipient contact
            recipient = self._get_recipient(request.user_id, request.delivery_method)
            
            # Create OTP entity
            otp = OTP(
                user_id=request.user_id,
                code=otp_code,
                delivery_method=DeliveryMethod(request.delivery_method),
                recipient=recipient,
                expires_in_minutes=5,
                max_attempts=3,
            )
            
            # Store OTP (mock - in real implementation, save to database)
            self.otp_storage[request.user_id] = otp
            
            # Mock: Mark as sent (in real implementation, send via email/SMS service)
            otp.mark_as_sent()
            
            logger.info(
                f"OTP generated successfully for user {request.user_id}. "
                f"OTP ID: {otp.otp_id}, Code: {otp_code} (MOCK - do not log in production)"
            )
            
            # Return response with masked recipient
            # DEVELOPMENT MODE: Include OTP code for testing
            return GenerateOTPResponse(
                otp_id=str(otp.otp_id),
                expires_at=otp.expires_at.isoformat(),
                delivery_method=request.delivery_method,
                recipient=self._mask_recipient(recipient, request.delivery_method),
                otp_code=otp_code,  # Only for development/testing
            )
            
        except Exception as e:
            logger.error(f"Failed to generate OTP for user {request.user_id}: {str(e)}")
            raise OTPGenerationFailedException(request.user_id, str(e))


__all__ = ["GenerateOTPUseCase"]
