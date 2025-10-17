"""Database adapter configuration for auth_microservice."""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for ORM models."""
    
    pass


class DatabaseAdapter:
    """
    Database adapter for managing SQLAlchemy async engine and sessions.
    Handles connection pooling, session management, and database lifecycle.
    """
    
    _instance: Optional["DatabaseAdapter"] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker] = None
    
    def __new__(cls) -> "DatabaseAdapter":
        """Singleton pattern for DatabaseAdapter."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(
        cls,
        database_url: str,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_pre_ping: bool = True,
        timeout: int = 10,
    ) -> "DatabaseAdapter":
        """
        Initialize the database adapter with async engine.
        
        Args:
            database_url: Database connection URL
            echo: Enable SQL logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_pre_ping: Test connections before using
            timeout: Connection timeout in seconds
            
        Returns:
            DatabaseAdapter instance
        """
        instance = cls()
        
        if instance._engine is not None:
            logger.warning("DatabaseAdapter already initialized")
            return instance
        
        try:
            logger.info(f"Initializing database connection: {database_url[:50]}...")
            
            # Determine pool class based on database type
            pool_class = NullPool if "sqlite" in database_url else QueuePool
            
            # Create async engine
            instance._engine = create_async_engine(
                database_url,
                echo=echo,
                future=True,
                pool_pre_ping=pool_pre_ping,
                pool_size=pool_size,
                max_overflow=max_overflow,
                poolclass=pool_class,
                connect_args={"timeout": timeout},
            )
            
            # Create async session factory
            instance._session_factory = async_sessionmaker(
                instance._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            
            logger.info("✅ Database adapter initialized successfully")
            return instance
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            instance._engine = None
            instance._session_factory = None
            raise
    
    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """
        Get the async engine instance.
        
        Returns:
            AsyncEngine instance
            
        Raises:
            RuntimeError: If adapter not initialized
        """
        instance = cls()
        if instance._engine is None:
            raise RuntimeError(
                "DatabaseAdapter not initialized. Call initialize() first."
            )
        return instance._engine
    
    @classmethod
    def get_session_factory(cls) -> async_sessionmaker:
        """
        Get the session factory.
        
        Returns:
            async_sessionmaker instance
            
        Raises:
            RuntimeError: If adapter not initialized
        """
        instance = cls()
        if instance._session_factory is None:
            raise RuntimeError(
                "DatabaseAdapter not initialized. Call initialize() first."
            )
        return instance._session_factory
    
    @classmethod
    async def get_session(cls) -> AsyncSession:
        """
        Get an async database session.
        
        Returns:
            AsyncSession instance
            
        Raises:
            RuntimeError: If adapter not initialized
        """
        factory = cls.get_session_factory()
        return factory()
    
    @classmethod
    async def create_tables(cls) -> None:
        """
        Create all database tables.
        
        Raises:
            RuntimeError: If adapter not initialized
        """
        engine = cls.get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created")
    
    @classmethod
    async def drop_tables(cls) -> None:
        """
        Drop all database tables.
        
        Warning: This is destructive and should only be used in testing/development.
        
        Raises:
            RuntimeError: If adapter not initialized
        """
        engine = cls.get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("⚠️  Database tables dropped")
    
    @classmethod
    async def dispose(cls) -> None:
        """
        Dispose of all connections and cleanup.
        
        Should be called on application shutdown.
        """
        instance = cls()
        if instance._engine is not None:
            await instance._engine.dispose()
            instance._engine = None
            instance._session_factory = None
            logger.info("✅ Database connections disposed")
    
    @classmethod
    async def health_check(cls) -> bool:
        """
        Perform a database health check.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            engine = cls.get_engine()
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
