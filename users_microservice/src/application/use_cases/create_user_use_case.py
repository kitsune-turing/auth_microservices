"""Create User Use Case."""
import logging
from uuid import UUID

from src.core.ports.repository_ports import UserRepositoryPort, PasswordServicePort
from src.application.dtos import CreateUserRequest, CreateUserResponse

logger = logging.getLogger(__name__)


class CreateUserUseCase:
    """
    Use case for creating a new user.
    
    Only ROOT users can create users (enforced in controller).
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_service: PasswordServicePort,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
    
    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """
        Create a new user.
        
        Args:
            request: Create user request data
            
        Returns:
            CreateUserResponse with user ID
            
        Raises:
            Exception if username or email already exists
        """
        logger.info(f"Creating user: {request.username}")
        
        # 1. Check if user already exists
        if await self.user_repository.user_exists(
            username=request.username,
            email=request.email
        ):
            logger.error(f"User already exists: {request.username} or {request.email}")
            raise Exception("Username or email already exists")
        
        # 2. Hash password
        password_hash = self.password_service.hash_password(request.password)
        
        # 3. Create user
        user_id = await self.user_repository.create_user(
            username=request.username,
            email=request.email,
            password_hash=password_hash,
            name=request.name,
            last_name=request.last_name,
            role=request.role,
            team_name=request.team_name,
        )
        
        logger.info(f"User created successfully: {request.username} (id={user_id})")
        
        return CreateUserResponse(
            id=user_id,
            username=request.username,
            email=request.email,
        )


__all__ = ["CreateUserUseCase"]
