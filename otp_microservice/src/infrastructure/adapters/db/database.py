"""Database configuration and connection management."""
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """Database adapter for managing database connections."""
    
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None
    
    @classmethod
    def initialize(
        cls,
        database_url: str,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_pre_ping: bool = True,
        timeout: int = 10,
    ) -> None:
        """
        Initialize database connection.
        
        Args:
            database_url: Database connection URL
            echo: Enable SQL query logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_pre_ping: Test connections before using
            timeout: Connection timeout in seconds
        """
        if cls._engine is not None:
            logger.warning("Database already initialized")
            return
        
        logger.info(f"Initializing database connection to {database_url.split('@')[1]}")
        
        cls._engine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            connect_args={"timeout": timeout},
        )
        
        cls._session_factory = async_sessionmaker(
            cls._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        logger.info("Database connection initialized successfully")
    
    @classmethod
    async def create_tables(cls) -> None:
        """Create all tables in the database."""
        if cls._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        logger.info("Creating database tables...")
        async with cls._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    @classmethod
    async def get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session.
        
        Yields:
            Database session
        """
        if cls._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with cls._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @classmethod
    async def close(cls) -> None:
        """Close database connection."""
        if cls._engine is not None:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            logger.info("Database connection closed")


__all__ = ["DatabaseAdapter"]
