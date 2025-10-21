"""Dependency Injection for Users Microservice.

Factory functions for creating use cases with their dependencies.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.database import get_db_session
from src.infrastructure.db.repository.user_repository import UserRepository
from src.infrastructure.adapters.services.password_service import BcryptPasswordService
from src.infrastructure.adapters.jano_client import get_jano_client, JANOClient

from src.application.use_cases.validate_credentials_use_case import ValidateCredentialsUseCase
from src.application.use_cases.validate_credentials_by_email_use_case import ValidateCredentialsByEmailUseCase
from src.application.use_cases.get_user_use_case import GetUserUseCase
from src.application.use_cases.get_user_by_email_use_case import GetUserByEmailUseCase
from src.application.use_cases.create_user_use_case import CreateUserUseCase
from src.application.use_cases.update_user_use_case import UpdateUserUseCase
from src.application.use_cases.get_users_use_case import GetUsersUseCase
from src.application.use_cases.disable_user_use_case import DisableUserUseCase
from src.application.use_cases.enable_user_use_case import EnableUserUseCase


# ============================================================================
# Repository Dependencies
# ============================================================================

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(session)


# ============================================================================
# Service Dependencies
# ============================================================================

def get_password_service() -> BcryptPasswordService:
    """Get password service instance."""
    return BcryptPasswordService(rounds=12)


# ============================================================================
# Use Case Dependencies
# ============================================================================

def get_validate_credentials_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> ValidateCredentialsUseCase:
    """Get validate credentials use case."""
    return ValidateCredentialsUseCase(user_repository, password_service)


def get_get_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUserUseCase:
    """Get user by ID use case."""
    return GetUserUseCase(user_repository)


def get_create_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> CreateUserUseCase:
    """Get create user use case."""
    jano_client = get_jano_client()
    return CreateUserUseCase(user_repository, password_service, jano_client)


def get_validate_credentials_by_email_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> ValidateCredentialsByEmailUseCase:
    """Get validate credentials by email use case."""
    return ValidateCredentialsByEmailUseCase(user_repository, password_service)


def get_user_by_email_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUserByEmailUseCase:
    """Get user by email use case."""
    return GetUserByEmailUseCase(user_repository)


def get_update_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UpdateUserUseCase:
    """Get update user use case."""
    return UpdateUserUseCase(user_repository)


def get_get_users_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUsersUseCase:
    """Get list users use case."""
    return GetUsersUseCase(user_repository)


def get_disable_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
) -> DisableUserUseCase:
    """Get disable user use case."""
    return DisableUserUseCase(user_repository)


def get_enable_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
) -> EnableUserUseCase:
    """Get enable user use case."""
    return EnableUserUseCase(user_repository)


__all__ = [
    "get_user_repository",
    "get_password_service",
    "get_validate_credentials_use_case",
    "get_validate_credentials_by_email_use_case",
    "get_get_user_use_case",
    "get_user_by_email_use_case",
    "get_create_user_use_case",
    "get_update_user_use_case",
    "get_get_users_use_case",
    "get_disable_user_use_case",
    "get_enable_user_use_case",
]
