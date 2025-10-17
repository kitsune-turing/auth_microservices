"""Test suite for auth_microservice entities and database configuration."""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator

from src.core.domain.entity import AuthToken, Session, TokenType
from src.infrastructure.db import DatabaseAdapter, Base, get_db_session
from src.core.config import TestConfig


# ============================================================================
# DOMAIN ENTITY TESTS
# ============================================================================

class TestAuthToken:
    """Test cases for AuthToken entity."""
    
    def test_auth_token_creation(self):
        """Test creating an AuthToken."""
        user_id = uuid4()
        token_string = "test_token_123"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        token = AuthToken(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_string=token_string,
            expires_at=expires_at,
        )
        
        assert token.user_id == user_id
        assert token.token_type == TokenType.ACCESS
        assert token.token_string == token_string
        assert token.revoked is False
        assert token.id is not None
    
    def test_auth_token_is_valid(self):
        """Test token validity check."""
        user_id = uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        token = AuthToken(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_string="valid_token",
            expires_at=expires_at,
        )
        
        assert token.is_valid() is True
        assert token.is_expired() is False
    
    def test_auth_token_is_expired(self):
        """Test expired token detection."""
        user_id = uuid4()
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        
        token = AuthToken(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_string="expired_token",
            expires_at=expires_at,
        )
        
        assert token.is_expired() is True
        assert token.is_valid() is False
    
    def test_auth_token_revoke(self):
        """Test token revocation."""
        user_id = uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        token = AuthToken(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            token_string="revoked_token",
            expires_at=expires_at,
        )
        
        assert token.is_valid() is True
        token.revoke()
        assert token.revoked is True
        assert token.is_valid() is False
    
    def test_auth_token_type_validation(self):
        """Test AuthToken type validation."""
        user_id = uuid4()
        
        with pytest.raises(TypeError):
            AuthToken(
                user_id="not_a_uuid",  # Invalid type
                token_type=TokenType.ACCESS,
                token_string="token",
                expires_at=datetime.now(timezone.utc),
            )
    
    def test_auth_token_empty_string_validation(self):
        """Test AuthToken empty string validation."""
        user_id = uuid4()
        
        with pytest.raises(ValueError):
            AuthToken(
                user_id=user_id,
                token_type=TokenType.ACCESS,
                token_string="",  # Empty string
                expires_at=datetime.now(timezone.utc),
            )
    
    def test_auth_token_repr(self):
        """Test token string representation."""
        user_id = uuid4()
        token = AuthToken(
            user_id=user_id,
            token_type=TokenType.SESSION,
            token_string="test_token",
            expires_at=datetime.now(timezone.utc),
        )
        
        repr_str = repr(token)
        assert "AuthToken" in repr_str
        assert str(user_id) in repr_str
    
    def test_auth_token_equality(self):
        """Test token equality based on ID."""
        user_id = uuid4()
        token_id = uuid4()
        
        token1 = AuthToken(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_string="token1",
            expires_at=datetime.now(timezone.utc),
            token_id=token_id,
        )
        
        token2 = AuthToken(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_string="token2",
            expires_at=datetime.now(timezone.utc),
            token_id=token_id,
        )
        
        assert token1 == token2
    
    def test_auth_token_hash(self):
        """Test token hashing."""
        user_id = uuid4()
        token = AuthToken(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_string="test_token",
            expires_at=datetime.now(timezone.utc),
        )
        
        # Token should be hashable and usable in sets
        token_set = {token}
        assert token in token_set


class TestSession:
    """Test cases for Session entity."""
    
    def test_session_creation(self):
        """Test creating a Session."""
        user_id = uuid4()
        token_id = uuid4()
        
        session = Session(
            user_id=user_id,
            access_token_id=token_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        
        assert session.user_id == user_id
        assert session.access_token_id == token_id
        assert session.ip_address == "192.168.1.1"
        assert session.active is True
        assert session.id is not None
    
    def test_session_is_valid(self):
        """Test session validity check."""
        user_id = uuid4()
        token_id = uuid4()
        
        session = Session(
            user_id=user_id,
            access_token_id=token_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        
        assert session.is_valid() is True
        assert session.is_expired() is False
    
    def test_session_is_expired(self):
        """Test expired session detection."""
        user_id = uuid4()
        token_id = uuid4()
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        
        session = Session(
            user_id=user_id,
            access_token_id=token_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            expires_at=expires_at,
        )
        
        assert session.is_expired() is True
        assert session.is_valid() is False
    
    def test_session_update_activity(self):
        """Test session activity update."""
        user_id = uuid4()
        token_id = uuid4()
        
        session = Session(
            user_id=user_id,
            access_token_id=token_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        
        original_activity = session.last_activity
        session.update_activity()
        
        assert session.last_activity > original_activity
    
    def test_session_end(self):
        """Test ending a session."""
        user_id = uuid4()
        token_id = uuid4()
        
        session = Session(
            user_id=user_id,
            access_token_id=token_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        
        assert session.active is True
        session.end_session()
        assert session.active is False
        assert session.is_valid() is False
    
    def test_session_type_validation(self):
        """Test Session type validation."""
        with pytest.raises(TypeError):
            Session(
                user_id="not_a_uuid",  # Invalid type
                access_token_id=uuid4(),
                ip_address="192.168.1.1",
                user_agent="Mozilla/5.0",
            )
    
    def test_session_repr(self):
        """Test session string representation."""
        user_id = uuid4()
        session = Session(
            user_id=user_id,
            access_token_id=uuid4(),
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        
        repr_str = repr(session)
        assert "Session" in repr_str
        assert str(user_id) in repr_str


# ============================================================================
# DATABASE ADAPTER TESTS
# ============================================================================

@pytest.fixture
async def db_adapter():
    """Fixture for database adapter."""
    adapter = DatabaseAdapter.initialize(
        database_url=TestConfig.DATABASE_URL,
        echo=True,
    )
    
    await adapter.create_tables()
    
    yield adapter
    
    await adapter.drop_tables()
    await adapter.dispose()


@pytest.mark.asyncio
async def test_database_adapter_initialization(db_adapter):
    """Test database adapter initialization."""
    engine = DatabaseAdapter.get_engine()
    assert engine is not None


@pytest.mark.asyncio
async def test_database_health_check(db_adapter):
    """Test database health check."""
    health = await DatabaseAdapter.health_check()
    assert health is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_dependency_injection(db_adapter):
    """Test get_db_session dependency injection."""
    session_gen = get_db_session()
    session = await session_gen.__anext__()
    
    assert session is not None
    
    # Cleanup
    await session_gen.aclose()


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestConfiguration:
    """Test cases for configuration."""
    
    def test_test_config_has_sqlite_url(self):
        """Test that TestConfig uses SQLite in memory."""
        assert "sqlite" in TestConfig.DATABASE_URL.lower()
        assert "memory" in TestConfig.DATABASE_URL.lower()
    
    def test_config_env_isolation(self):
        """Test that configs are properly isolated."""
        # TestConfig should not affect default config
        assert TestConfig.ENV == "test"
        assert TestConfig.DEBUG is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
