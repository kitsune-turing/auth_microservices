"""OTP Controller."""
import logging
from fastapi import APIRouter, status

from src.application.dtos import (
    GenerateOTPRequest,
    GenerateOTPResponse,
    ValidateOTPRequest,
    ValidateOTPResponse,
)
from src.application.generate_otp_use_case import GenerateOTPUseCase
from src.application.validate_otp_use_case import ValidateOTPUseCase

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/otp",
    tags=["otp"],
)

# Shared storage for mock implementation
# In a real implementation, this would be a database
OTP_STORAGE = {}

# Initialize use cases with shared storage
generate_otp_use_case = GenerateOTPUseCase()
generate_otp_use_case.otp_storage = OTP_STORAGE

validate_otp_use_case = ValidateOTPUseCase(otp_storage=OTP_STORAGE)


@router.post(
    "/generate",
    response_model=GenerateOTPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate OTP",
    description=(
        "Generate a One-Time Password for user authentication. "
        "The OTP will be sent to the user's registered contact method (email/SMS). "
        "**Note: This is a mock implementation for development.**"
    ),
)
async def generate_otp(request: GenerateOTPRequest) -> GenerateOTPResponse:
    """
    Generate OTP for user.
    
    **Mock Implementation Details:**
    - Generates a random 6-digit code
    - Stores in memory (not persistent)
    - Does not actually send email/SMS
    - OTP code is logged for testing purposes
    
    **Production Implementation Would:**
    1. Store OTP in database
    2. Send via email service (SendGrid, AWS SES, etc.)
    3. Send via SMS service (Twilio, AWS SNS, etc.)
    4. Not log the actual OTP code
    
    Args:
        request: OTP generation request
        
    Returns:
        GenerateOTPResponse with OTP details
        
    Raises:
        400: Invalid request parameters
        500: OTP generation failed
    """
    logger.info(f"[MOCK] Generating OTP for user {request.user_id}")
    
    response = await generate_otp_use_case.execute(request)
    
    logger.info(
        f"[MOCK] OTP generated successfully for user {request.user_id}. "
        f"Check server logs for the actual code (development only)"
    )
    
    return response


@router.post(
    "/validate",
    response_model=ValidateOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate OTP",
    description=(
        "Validate a One-Time Password code for user authentication. "
        "Maximum 3 attempts allowed before OTP is invalidated. "
        "**Note: This is a mock implementation for development.**"
    ),
)
async def validate_otp(request: ValidateOTPRequest) -> ValidateOTPResponse:
    """
    Validate OTP code.
    
    **Mock Implementation Details:**
    - Validates against in-memory storage
    - Enforces attempt limits (3 max)
    - Checks expiration (5 minutes)
    
    **Production Implementation Would:**
    1. Query database for OTP
    2. Implement rate limiting
    3. Log validation attempts for security
    4. Invalidate OTP after successful validation
    
    Args:
        request: OTP validation request
        
    Returns:
        ValidateOTPResponse with validation result
        
    Raises:
        400: Invalid OTP code or OTP expired
        404: No OTP found for user
        429: Maximum attempts exceeded
    """
    logger.info(f"[MOCK] Validating OTP for user {request.user_id}")
    
    response = await validate_otp_use_case.execute(request)
    
    if response.is_valid:
        logger.info(f"[MOCK] OTP validated successfully for user {request.user_id}")
    else:
        logger.warning(f"[MOCK] OTP validation failed for user {request.user_id}")
    
    return response


__all__ = ["router"]
