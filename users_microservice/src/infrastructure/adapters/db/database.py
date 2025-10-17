"""Database configuration y base para SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Optional
import os

# URL de BD compartida desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/auth_login_services"
)

# Motor async para SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Cambia a True para ver queries SQL en logs
    future=True,
    pool_pre_ping=True,
)

# Session factory asincrónico
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base para todas las entidades ORM
Base = declarative_base()


async def get_db_session():
    """Dependency para inyectar sesión en endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Crea todas las tablas (solo en desarrollo)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Elimina todas las tablas (solo para testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
