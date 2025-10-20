"""OTP Controller."""
import logging
from fastapi import APIRouter, status, Depends

from src.core.ports import OTPRepositoryPort
from src.application.dtos import (
    GenerateOTPRequest,
    GenerateOTPResponse,
    ValidateOTPRequest,
    ValidateOTPResponse,
)
from src.application.generate_otp_use_case import GenerateOTPUseCase
from src.application.validate_otp_use_case import ValidateOTPUseCase
from src.infrastructure.dependencies import get_otp_repository

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/otp",
    tags=["otp"],
)


@router.post(
    "/generate",
    response_model=GenerateOTPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate OTP",
    description=(
        "Generate a One-Time Password for user authentication. "
        "The OTP will be sent to the user's registered contact method (email/SMS). "
        "**Stored in database for persistence.**"
    ),
)
async def generate_otp(
    request: GenerateOTPRequest,
    otp_repository: OTPRepositoryPort = Depends(get_otp_repository),
) -> GenerateOTPResponse:
    """
    Generate OTP for user.
    
    **Implementation Details:**
    - Generates a random 6-digit code
    - Stores in PostgreSQL database
    - Expires in 5 minutes (configurable)
    - Maximum 3 validation attempts
    
    **Development Mode:**
    - OTP code is included in response for testing
    - Email/SMS sending is skipped
    
    **Production Implementation Would:**
    1. Send via email service (SendGrid, AWS SES, etc.)
    2. Send via SMS service (Twilio, AWS SNS, etc.)
    3. Not include OTP code in response
    
    Args:
        request: OTP generation request
        otp_repository: OTP repository (injected)
        
    Returns:
        GenerateOTPResponse with OTP details
        
    Raises:
        400: Invalid request parameters
        500: OTP generation failed
    """
    logger.info(f"Generating OTP for user {request.user_id}")
    
    use_case = GenerateOTPUseCase(otp_repository)
    response = await use_case.execute(request)
    
    logger.info(f"OTP generated successfully for user {request.user_id}")
    
    return response


@router.post(
    "/validate",
    response_model=ValidateOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate OTP",
    description=(
        "Validate a One-Time Password code for user authentication. "
        "Maximum 3 attempts allowed before OTP is invalidated. "
        "**Stored in database for persistence.**"
    ),
)
async def validate_otp(
    request: ValidateOTPRequest,
    otp_repository: OTPRepositoryPort = Depends(get_otp_repository),
) -> ValidateOTPResponse:
    """
    Validate OTP code.
    
    **Implementation Details:**
    - Validates against PostgreSQL database
    - Enforces attempt limits (3 max)
    - Checks expiration (5 minutes)
    - Marks OTP as validated on success
    
    **Production Implementation Would:**
    1. Query database for OTP
    2. Implement rate limiting
    3. Log validation attempts for security
    4. Invalidate OTP after successful validation
    
    Args:
        request: OTP validation request
        otp_repository: OTP repository (injected)
        
    Returns:
        ValidateOTPResponse with validation result
        
    Raises:
        400: Invalid OTP code or OTP expired
        404: No OTP found for user
        429: Maximum attempts exceeded
    """
    logger.info(f"Validating OTP with otp_id: {request.otp_id}")
    
    use_case = ValidateOTPUseCase(otp_repository)
    response = await use_case.execute(request)
    
    if response.valid:
        logger.info(f"OTP validated successfully for otp_id: {request.otp_id}")
    else:
        logger.warning(f"OTP validation failed for otp_id: {request.otp_id}")
    
    return response


__all__ = ["router"]
