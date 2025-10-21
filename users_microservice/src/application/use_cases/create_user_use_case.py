"""Create User Use Case."""
import logging
from uuid import UUID

from src.core.ports.repository_ports import UserRepositoryPort, PasswordServicePort
from src.application.dtos import CreateUserRequest, CreateUserResponse
from src.infrastructure.adapters.jano_client import JANOClient, JANOValidationError

logger = logging.getLogger(__name__)


class CreateUserUseCase:
    """
    Use case for creating a new user.
    
    Only ROOT users can create users (enforced in controller).
    Validates password and username against JANO security policies.
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_service: PasswordServicePort,
        jano_client: JANOClient,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jano_client = jano_client
    
    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """
        Create a new user.
        
        Args:
            request: Create user request data
            
        Returns:
            CreateUserResponse with user ID
            
        Raises:
            ValueError: If username or email already exists
            JANOValidationError: If password/username don't meet security policies
        """
        logger.info(f"Creating user: {request.username}")
        
        # 1. Validate username with JANO
        logger.debug(f"Validating username with JANO: {request.username}")
        username_valid, username_violations = await self.jano_client.validate_username(
            username=request.username
        )
        
        if not username_valid:
            violations_msg = "; ".join(username_violations)
            logger.warning(
                f"Username validation failed for '{request.username}': {violations_msg}"
            )
            raise JANOValidationError(
                f"Username does not meet security requirements: {violations_msg}",
                username_violations
            )
        
        # 2. Validate password with JANO
        logger.debug(f"Validating password with JANO for user: {request.username}")
        password_valid, password_violations = await self.jano_client.validate_password(
            password=request.password,
            username=request.username
        )
        
        if not password_valid:
            violations_msg = "; ".join(password_violations)
            logger.warning(
                f"Password validation failed for '{request.username}': {violations_msg}"
            )
            raise JANOValidationError(
                f"Password does not meet security requirements: {violations_msg}",
                password_violations
            )
        
        # 3. Check if user already exists
        if await self.user_repository.user_exists(
            username=request.username,
            email=request.email
        ):
            logger.error(f"User already exists: {request.username} or {request.email}")
            raise ValueError("Username or email already exists")
        
        # 4. Hash password
        password_hash = self.password_service.hash_password(request.password)
        
        # 5. Create user
        user_id = await self.user_repository.create_user(
            username=request.username,
            email=request.email,
            password_hash=password_hash,
            name=request.name,
            last_name=request.last_name,
            role=request.role,
            team_id=request.team_id,
        )
        
        logger.info(
            f"User created successfully: {request.username} (id={user_id}) "
            f"[JANO validated]"
        )
        
        return CreateUserResponse(
            id=user_id,
            username=request.username,
            email=request.email,
        )


__all__ = ["CreateUserUseCase"]
