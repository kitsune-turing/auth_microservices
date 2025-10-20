"""Database configuration and session management for Users Microservice."""
import logging
import os
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from .models import Base

logger = logging.getLogger(__name__)


# ============================================================================
# Database Configuration
# ============================================================================

def get_database_url() -> str:
    """Get database URL from environment variables."""
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        # Build from components
        db_user = os.getenv("DATABASE_USER", "admin")
        db_password = os.getenv("DATABASE_PASSWORD", "secure_password_123")
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "auth_login_services")
        
        db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    logger.info(f"Database URL configured: {db_url.split('@')[0]}@...")
    return db_url


# Create async engine
DATABASE_URL = get_database_url()
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    poolclass=NullPool,  # Disable connection pooling for async
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ============================================================================
# Database Session Dependency
# ============================================================================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    
    Usage in FastAPI:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()


# ============================================================================
# Database Initialization
# ============================================================================

async def setup_database() -> None:
    """
    Verify database connection.
    
    Database tables are created by the centralized schema.sql initialization script.
    Do not attempt to create them again to avoid permission errors and conflicts.
    
    This should be called during application startup.
    """
    try:
        async with engine.begin() as conn:
            # Just verify connection
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        raise


async def close_database() -> None:
    """
    Close database connections.
    
    This should be called during application shutdown.
    """
    try:
        await engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Database close failed: {str(e)}")
        raise


__all__ = [
    "get_db_session",
    "setup_database",
    "close_database",
    "engine",
    "AsyncSessionLocal",
]
