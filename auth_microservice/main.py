"""Auth Microservice - Main Application.

Authentication and authorization microservice using hexagonal architecture.
Integrates with users_microservice and otp_microservice.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.adapters.controllers import router as auth_router
from src.infrastructure.middleware import register_exception_handlers
from src.infrastructure.config.settings import settings
from src.infrastructure.adapters.db.db_adapter import DatabaseAdapter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("=" * 60)
    logger.info(" AUTH MICROSERVICE STARTING")
    logger.info("=" * 60)
    logger.info(f"Service Name: {settings.SERVICE_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Port: {settings.SERVICE_PORT}")
    logger.info(f"JWT Algorithm: {settings.JWT_ALGORITHM}")
    logger.info(f"Access Token Expiration: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    logger.info(f"Refresh Token Expiration: {settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS} days")
    logger.info("=" * 60)
    
    # Initialize database
    try:
        logger.info("Initializing database connection...")
        DatabaseAdapter.initialize(
            database_url=settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
            timeout=settings.DATABASE_TIMEOUT,
        )
        logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("=" * 60)
    logger.info(" AUTH MICROSERVICE SHUTTING DOWN")
    logger.info("=" * 60)
    await DatabaseAdapter.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.SERVICE_NAME,
    description=(
        "Authentication and Authorization microservice. "
        "Handles user login, token generation, and token validation. "
        "Built with hexagonal architecture pattern."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(auth_router, prefix="/api")


@app.get("/", tags=["health"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
        log_level="info",
    )
