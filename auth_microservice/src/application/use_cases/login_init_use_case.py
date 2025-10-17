"""Login Init Use Case - Step 1: Validate credentials and send OTP."""
import logging

from src.domain.ports import UsersServicePort, OTPServicePort
from src.domain.exceptions import InvalidCredentialsException
from src.application.dtos import LoginRequest, LoginInitResponse

logger = logging.getLogger(__name__)


class LoginInitUseCase:
    """Use case for initiating login - validates credentials and sends OTP."""
    
    def __init__(
        self,
        users_service: UsersServicePort,
        otp_service: OTPServicePort,
    ):
        """Initialize login init use case."""
        self.users_service = users_service
        self.otp_service = otp_service
    
    async def execute(self, request: LoginRequest) -> LoginInitResponse:
        """
        Execute login initialization.
        
        Args:
            request: Login request with email and password
            
        Returns:
            LoginInitResponse with OTP sent confirmation
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        logger.info(f"Login init attempt for email: {request.email}")
        
        # Step 1: Validate credentials via users_microservice
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
        
        # Step 2: Generate and send OTP via email
        otp_response = await self.otp_service.generate_otp(
            user_id=user_id,
            delivery_method="email",
        )
        
        logger.info(f"OTP sent to email for user: {user_id}")
        
        # Step 3: Mask email for security
        masked_email = self._mask_email(email)
        
        return LoginInitResponse(
            message="OTP sent to your email",
            email=masked_email,
            otp_id=otp_response["otp_id"],
            expires_in=300,  # 5 minutes
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
