"""Configuration module for auth_microservice.

This module provides centralized configuration management for the authentication
microservice, including database settings, JWT configuration, and environment
settings.

All configuration values are loaded from environment variables with sensible defaults.
"""
import os
import logging
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class Config:
    """Base configuration class with default settings."""
    
    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    
    @staticmethod
    def _build_database_url() -> str:
        """
        Build database URL from environment variables.
        
        Supports multiple formats:
        - Direct DATABASE_URL environment variable
        - Individual components (USER, PASSWORD, HOST, PORT, NAME)
        - Defaults to local PostgreSQL
        
        Returns:
            Database connection URL
        """
        # Check for direct database URL first
        direct_url = os.getenv("DATABASE_URL")
        if direct_url:
            return direct_url
        
        # Build from components
        db_user = os.getenv("DATABASE_USER", "admin")
        db_password = os.getenv("DATABASE_PASSWORD", "secure_password_123")
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "auth_login_services")
        
        return (
            f"postgresql+asyncpg://{db_user}:{db_password}@"
            f"{db_host}:{db_port}/{db_name}"
        )
    
    DATABASE_URL: str = _build_database_url.__func__()
    
    # Database connection pool settings
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    DATABASE_POOL_PRE_PING: bool = os.getenv("DATABASE_POOL_PRE_PING", "true").lower() == "true"
    DATABASE_TIMEOUT: int = int(os.getenv("DATABASE_TIMEOUT", "10"))
    
    # ============================================================================
    # JWT CONFIGURATION
    # ============================================================================
    
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "your_secret_key_here_change_in_production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # ============================================================================
    # ENVIRONMENT & LOGGING
    # ============================================================================
    
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = ENV.lower() == "development"
    
    # ============================================================================
    # SERVICE METADATA
    # ============================================================================
    
    SERVICE_NAME: str = "auth_microservice"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8001"))
    
    # ============================================================================
    # MICROSERVICE INTEGRATION
    # ============================================================================
    
    # Users Microservice
    USERS_SERVICE_URL: str = os.getenv(
        "USERS_SERVICE_URL",
        "http://users_microservice:8006"
    )
    USERS_SERVICE_TIMEOUT: int = int(os.getenv("USERS_SERVICE_TIMEOUT", "10"))
    
    # OTP Microservice
    OTP_SERVICE_URL: str = os.getenv(
        "OTP_SERVICE_URL",
        "http://otp_microservice:8005"
    )
    OTP_SERVICE_TIMEOUT: int = int(os.getenv("OTP_SERVICE_TIMEOUT", "5"))
    
    # ============================================================================
    # CORS CONFIGURATION
    # ============================================================================
    
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG: bool = True
    ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG: bool = False
    ENV: str = "production"
    LOG_LEVEL: str = "INFO"


class TestConfig(Config):
    """Test environment configuration."""
    
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    DEBUG: bool = True
    ENV: str = "test"
    LOG_LEVEL: str = "WARNING"


def get_config() -> Config:
    """
    Get configuration instance based on ENV environment variable.
    
    Returns:
        Config instance (DevelopmentConfig, ProductionConfig, or TestConfig)
    """
    env = os.getenv("ENV", "development").lower()
    
    configs = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig,
        "test": TestConfig,
        "testing": TestConfig,
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    logger.info(f"Loaded configuration: {config_class.__name__}")
    return config_class()


# Global config singleton
config: Config = get_config()

# ============================================================================
# DATABASE ADAPTER LAZY LOADING
# ============================================================================

def get_database_adapter():
    """
    Lazy load and return the DatabaseAdapter instance.
    
    This is imported here to avoid circular imports since DatabaseAdapter
    imports from this module.
    
    Returns:
        DatabaseAdapter instance
    """
    from src.infrastructure.adapters.db.db_adapter import DatabaseAdapter
    
    return DatabaseAdapter


# Export configuration
__all__ = [
    "Config",
    "DevelopmentConfig",
    "ProductionConfig",
    "TestConfig",
    "config",
    "get_config",
    "get_database_adapter",
]

