"""Validate OTP Use Case."""
import logging
from datetime import datetime, UTC

from src.core.domain.exceptions import (
    OTPNotFoundException,
    OTPExpiredException,
    InvalidOTPCodeException,
    MaxAttemptsExceededException,
    OTPAlreadyUsedException,
)
from src.application.dtos import ValidateOTPRequest, ValidateOTPResponse

logger = logging.getLogger(__name__)


class ValidateOTPUseCase:
    """Use case for validating OTP."""
    
    def __init__(self, otp_storage: dict = None):
        """Initialize use case."""
        self.otp_storage = otp_storage if otp_storage is not None else {}
    
    async def execute(self, request: ValidateOTPRequest) -> ValidateOTPResponse:
        """
        Validate OTP code for user.
        
        Args:
            request: OTP validation request
            
        Returns:
            ValidateOTPResponse with validation result
            
        Raises:
            OTPNotFoundException: If no OTP found for user
            OTPExpiredException: If OTP has expired
            OTPAlreadyUsedException: If OTP was already validated
            MaxAttemptsExceededException: If max attempts exceeded
        """
        logger.info(f"Validating OTP for user {request.user_id}")
        
        # Get OTP for user
        otp = self.otp_storage.get(request.user_id)
        
        if not otp:
            logger.warning(f"No OTP found for user {request.user_id}")
            raise OTPNotFoundException(request.user_id)
        
        # Check if already validated
        if otp.status.value == "validated":
            logger.warning(f"OTP already used for user {request.user_id}")
            raise OTPAlreadyUsedException(str(otp.otp_id))
        
        # Check if expired
        if otp.is_expired():
            otp.mark_as_expired()
            logger.warning(f"OTP expired for user {request.user_id}")
            raise OTPExpiredException(str(otp.otp_id))
        
        # Check if max attempts exceeded
        if not otp.can_attempt_validation():
            logger.warning(f"Max OTP attempts exceeded for user {request.user_id}")
            raise MaxAttemptsExceededException(request.user_id)
        
        # Increment attempts
        otp.increment_attempts()
        
        # Validate code
        if otp.is_valid_code(request.otp_code):
            otp.mark_as_validated()
            logger.info(f"OTP validated successfully for user {request.user_id}")
            
            return ValidateOTPResponse(
                is_valid=True,
                message="OTP validated successfully",
                attempts_remaining=None,
            )
        else:
            attempts_remaining = otp.max_attempts - otp.attempts
            logger.warning(
                f"Invalid OTP code for user {request.user_id}. "
                f"Attempts remaining: {attempts_remaining}"
            )
            
            if attempts_remaining == 0:
                raise MaxAttemptsExceededException(request.user_id)
            
            raise InvalidOTPCodeException(attempts_remaining)


__all__ = ["ValidateOTPUseCase"]
