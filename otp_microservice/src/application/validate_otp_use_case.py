"""Validate OTP Use Case."""
import logging
from datetime import datetime, UTC
from uuid import UUID

from src.core.ports import OTPRepositoryPort
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
    
    def __init__(self, otp_repository: OTPRepositoryPort):
        """
        Initialize use case.
        
        Args:
            otp_repository: OTP repository implementation
        """
        self.otp_repository = otp_repository
    
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
        logger.info(f"Validating OTP with otp_id {request.otp_id}")
        
        # Get OTP from database
        otp = await self.otp_repository.get_by_id(UUID(request.otp_id))
        
        if not otp:
            logger.warning(f"No OTP found with otp_id {request.otp_id}")
            raise OTPNotFoundException(request.otp_id)
        
        # Check if already validated
        if otp.status.value == "validated":
            logger.warning(f"OTP already used: {request.otp_id}")
            raise OTPAlreadyUsedException(request.otp_id)
        
        # Check if expired
        if otp.is_expired():
            otp.mark_as_expired()
            logger.warning(f"OTP expired: {request.otp_id}")
            raise OTPExpiredException(request.otp_id)
        
        # Check if max attempts exceeded
        if not otp.can_attempt_validation():
            logger.warning(f"Max OTP attempts exceeded for otp_id {request.otp_id}")
            raise MaxAttemptsExceededException(request.otp_id)
        
        # Increment attempts
        otp.increment_attempts()
        
        # Validate code
        if otp.is_valid_code(request.otp_code):
            otp.mark_as_validated()
            await self.otp_repository.update(otp)
            logger.info(f"OTP validated successfully: {request.otp_id}")
            
            return ValidateOTPResponse(
                valid=True,
                user_id=otp.user_id,
                email=otp.recipient if "@" in otp.recipient else None,
                message="OTP validated successfully",
                attempts_remaining=None,
            )
        else:
            # Update attempts in database
            await self.otp_repository.update(otp)
            
            attempts_remaining = otp.max_attempts - otp.attempts
            logger.warning(
                f"Invalid OTP code for otp_id {request.otp_id}. "
                f"Attempts remaining: {attempts_remaining}"
            )
            
            if attempts_remaining == 0:
                raise MaxAttemptsExceededException(request.otp_id)
            
            raise InvalidOTPCodeException(attempts_remaining)


__all__ = ["ValidateOTPUseCase"]
