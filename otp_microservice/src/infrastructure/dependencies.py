"""Dependency injection for OTP microservice."""
import logging
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.ports import OTPRepositoryPort
from src.infrastructure.adapters.db import DatabaseAdapter, OTPRepository

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency.
    
    Yields:
        Database session
    """
    async for session in DatabaseAdapter.get_session():
        yield session


def get_otp_repository(
    session: AsyncSession = Depends(get_db_session),
) -> OTPRepositoryPort:
    """
    Get OTP repository dependency.
    
    Args:
        session: Database session (injected by FastAPI)
        
    Returns:
        OTP repository instance
    """
    return OTPRepository(session)


__all__ = [
    "get_db_session",
    "get_otp_repository",
]
