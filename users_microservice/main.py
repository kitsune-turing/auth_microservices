"""FastAPI application entry point - Users Microservice."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.db.database import setup_database, close_database
from src.infrastructure.adapters.controllers import auth_controller, user_controller
from src.infrastructure.middleware import register_exception_handlers, AuthMiddleware
import src.infrastructure.middleware.auth_middleware as auth_middleware_module

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Users Microservice...")
    await setup_database()
    logger.info("Database initialized successfully")
    
    # Initialize auth middleware
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://auth_microservice:8001")
    auth_middleware_module.auth_middleware = AuthMiddleware(auth_service_url)
    logger.info(f"Auth middleware initialized with URL: {auth_service_url}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Users Microservice...")
    await close_database()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Users Microservice",
    description="Microservicio de gestión de usuarios - Hexagonal Architecture",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(auth_controller.router)
app.include_router(user_controller.router)


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "service": "Users Microservice",
        "status": "healthy",
        "endpoints": {
            "validate_credentials": "POST /api/users/validate-credentials",
            "get_user": "GET /api/users/{user_id}",
            "create_user": "POST /api/users",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info",
    )
