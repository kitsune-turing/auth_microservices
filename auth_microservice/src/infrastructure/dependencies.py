"""FastAPI dependencies for database and repositories."""
import logging
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.db.db_adapter import DatabaseAdapter
from src.infrastructure.adapters.db.repositories import (
    AuthTokenRepository,
    SessionRepository,
)

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a database session.
    
    Yields:
        AsyncSession: Database session
    """
    session_factory = DatabaseAdapter.get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_token_repository(
    session: AsyncSession = Depends(get_db_session)
) -> AuthTokenRepository:
    """
    Dependency to get AuthTokenRepository.
    
    Args:
        session: Database session from dependency
        
    Returns:
        AuthTokenRepository instance
    """
    return AuthTokenRepository(session)


async def get_session_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SessionRepository:
    """
    Dependency to get SessionRepository.
    
    Args:
        session: Database session from dependency
        
    Returns:
        SessionRepository instance
    """
    return SessionRepository(session)


__all__ = [
    "get_db_session",
    "get_token_repository",
    "get_session_repository",
]
