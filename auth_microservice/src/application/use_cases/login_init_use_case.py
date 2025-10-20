"""Login Init Use Case - Step 1: Validate credentials and send OTP."""
import logging

from src.domain.ports import UsersServicePort, OTPServicePort, JANOServicePort
from src.domain.exceptions import (
    InvalidCredentialsException,
    RateLimitExceededException,
)
from src.application.dtos import LoginRequest, LoginInitResponse

logger = logging.getLogger(__name__)


class LoginInitUseCase:
    """Use case for initiating login - validates credentials and sends OTP."""
    
    def __init__(
        self,
        users_service: UsersServicePort,
        otp_service: OTPServicePort,
        jano_service: JANOServicePort,
    ):
        """Initialize login init use case."""
        self.users_service = users_service
        self.otp_service = otp_service
        self.jano_service = jano_service
    
    async def execute(
        self,
        request: LoginRequest,
        ip_address: str = "0.0.0.0",
        user_agent: str = "Unknown",
    ) -> LoginInitResponse:
        """
        Execute login initialization.
        
        Args:
            request: Login request with email and password
            ip_address: Client IP address for rate limiting
            user_agent: Client user agent
            
        Returns:
            LoginInitResponse with OTP sent confirmation
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
            RateLimitExceededException: If rate limit exceeded
        """
        logger.info(f"Login init attempt for email: {request.email}")
        
        # Step 1: Check rate limiting via JANO (before credential validation)
        try:
            rate_limit_result = await self.jano_service.validate_request(
                user_id="anonymous",  # Not authenticated yet
                role="anonymous",
                endpoint="/auth/login",
                method="POST",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            if rate_limit_result.get("should_block", False):
                violations = rate_limit_result.get("violated_rules", [])
                logger.warning(f"Rate limit exceeded for IP {ip_address}: {violations}")
                raise RateLimitExceededException(
                    details=f"Too many login attempts from IP {ip_address}"
                )
        except RateLimitExceededException:
            raise
        except Exception as e:
            # If JANO is unavailable, log but continue (graceful degradation)
            logger.warning(f"JANO rate limit check failed: {e}. Continuing without rate limit validation.")
        
        # Step 2: Validate credentials via users_microservice
        user_data = await self.users_service.validate_credentials_by_email(
            email=request.email,
            password=request.password,
        )
        
        if not user_data:
            logger.warning(f"Invalid credentials for email: {request.email}")
            raise InvalidCredentialsException("Invalid email or password")
        
        user_id = str(user_data["id"])
        email = user_data["email"]
        
        logger.info(f"Credentials valid for user: {user_id}")
        
        # Step 3: Generate and send OTP via email
        otp_response = await self.otp_service.generate_otp(
            user_id=user_id,
            delivery_method="email",
            recipient=email,  # Pass the real email address
        )
        
        logger.info(f"OTP sent to email for user: {user_id}")
        
        # Step 4: Mask email for security
        masked_email = self._mask_email(email)
        
        return LoginInitResponse(
            message="OTP sent to your email",
            email=masked_email,
            otp_id=otp_response["otp_id"],
            expires_in=300,  # 5 minutes
            otp_code=otp_response.get("otp_code"),  # Only in development mode
        )
    
    def _mask_email(self, email: str) -> str:
        """Mask email for privacy."""
        if "@" not in email:
            return email
        
        local, domain = email.split("@")
        if len(local) <= 2:
            masked_local = local[0] + "*"
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"


__all__ = ["LoginInitUseCase"]
