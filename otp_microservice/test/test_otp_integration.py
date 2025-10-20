"""
Integration tests for OTP microservice with database persistence.
"""
import pytest
import asyncio
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.domain.entity.otp import OTP
from src.core.domain.value_objects.delivery_method import DeliveryMethod
from src.core.domain.value_objects.otp_status import OTPStatus
from src.infrastructure.adapters.db.models import OTPModel
from src.infrastructure.adapters.db.database import DatabaseAdapter
from src.infrastructure.adapters.db.otp_repository import OTPRepository
from src.infrastructure.config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine():
    """Create a test database engine."""
    # Use test database URL
    test_db_url = settings.DATABASE_URL.replace(
        "auth_login_services", 
        "auth_login_services_test"
    )
    
    engine = create_async_engine(
        test_db_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create a database session for tests."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def otp_repository(db_session):
    """Create an OTP repository instance."""
    return OTPRepository(db_session)


@pytest.mark.asyncio
async def test_save_and_retrieve_otp(otp_repository):
    """Test saving and retrieving an OTP."""
    # Create OTP entity
    otp = OTP.create(
        user_id="test_user_123",
        code="123456",
        delivery_method=DeliveryMethod.EMAIL,
        recipient="test@example.com",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        max_attempts=3
    )
    
    # Save to database
    saved_otp = await otp_repository.save(otp)
    
    # Verify saved
    assert saved_otp.id is not None
    assert saved_otp.user_id == "test_user_123"
    assert saved_otp.code == "123456"
    assert saved_otp.status == OTPStatus.PENDING
    
    # Retrieve from database
    retrieved_otp = await otp_repository.get_by_id(saved_otp.id)
    
    assert retrieved_otp is not None
    assert retrieved_otp.id == saved_otp.id
    assert retrieved_otp.user_id == saved_otp.user_id
    assert retrieved_otp.code == saved_otp.code


@pytest.mark.asyncio
async def test_update_otp_status(otp_repository):
    """Test updating OTP status."""
    # Create and save OTP
    otp = OTP.create(
        user_id="test_user_456",
        code="654321",
        delivery_method=DeliveryMethod.SMS,
        recipient="+573001234567",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        max_attempts=3
    )
    saved_otp = await otp_repository.save(otp)
    
    # Mark as sent
    saved_otp.mark_as_sent()
    updated_otp = await otp_repository.update(saved_otp)
    
    assert updated_otp.status == OTPStatus.SENT
    assert updated_otp.sent_at is not None
    
    # Mark as validated
    updated_otp.mark_as_validated()
    final_otp = await otp_repository.update(updated_otp)
    
    assert final_otp.status == OTPStatus.VALIDATED
    assert final_otp.validated_at is not None


@pytest.mark.asyncio
async def test_increment_attempts(otp_repository):
    """Test incrementing validation attempts."""
    # Create and save OTP
    otp = OTP.create(
        user_id="test_user_789",
        code="987654",
        delivery_method=DeliveryMethod.EMAIL,
        recipient="test2@example.com",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        max_attempts=3
    )
    saved_otp = await otp_repository.save(otp)
    
    # Increment attempts
    for i in range(3):
        saved_otp.increment_attempts()
        await otp_repository.update(saved_otp)
    
    # Verify max attempts reached
    retrieved_otp = await otp_repository.get_by_id(saved_otp.id)
    assert retrieved_otp.attempts == 3
    assert retrieved_otp.has_exceeded_max_attempts()


@pytest.mark.asyncio
async def test_get_by_user_id(otp_repository):
    """Test retrieving OTPs by user ID."""
    user_id = "test_user_multi"
    
    # Create multiple OTPs for same user
    for i in range(3):
        otp = OTP.create(
            user_id=user_id,
            code=f"12345{i}",
            delivery_method=DeliveryMethod.EMAIL,
            recipient=f"test{i}@example.com",
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            max_attempts=3
        )
        await otp_repository.save(otp)
    
    # Retrieve all OTPs for user
    user_otps = await otp_repository.get_by_user_id(user_id)
    
    assert len(user_otps) >= 3
    assert all(otp.user_id == user_id for otp in user_otps)


@pytest.mark.asyncio
async def test_delete_expired_otps(otp_repository):
    """Test deleting expired OTPs."""
    # Create expired OTP
    expired_otp = OTP.create(
        user_id="test_user_expired",
        code="000000",
        delivery_method=DeliveryMethod.EMAIL,
        recipient="expired@example.com",
        expires_at=datetime.utcnow() - timedelta(minutes=10),  # Already expired
        max_attempts=3
    )
    await otp_repository.save(expired_otp)
    
    # Delete expired OTPs
    deleted_count = await otp_repository.delete_expired()
    
    assert deleted_count >= 1


@pytest.mark.asyncio
async def test_otp_expiration(otp_repository):
    """Test OTP expiration logic."""
    # Create OTP that will expire soon
    otp = OTP.create(
        user_id="test_user_expiry",
        code="111111",
        delivery_method=DeliveryMethod.EMAIL,
        recipient="expiry@example.com",
        expires_at=datetime.utcnow() + timedelta(seconds=1),
        max_attempts=3
    )
    saved_otp = await otp_repository.save(otp)
    
    # Verify not expired yet
    assert not saved_otp.is_expired()
    
    # Wait for expiration
    await asyncio.sleep(2)
    
    # Retrieve and check expiration
    retrieved_otp = await otp_repository.get_by_id(saved_otp.id)
    assert retrieved_otp.is_expired()


@pytest.mark.asyncio
async def test_otp_validation_flow(otp_repository):
    """Test complete OTP validation flow."""
    # 1. Create OTP
    otp = OTP.create(
        user_id="test_user_flow",
        code="555555",
        delivery_method=DeliveryMethod.EMAIL,
        recipient="flow@example.com",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        max_attempts=3
    )
    saved_otp = await otp_repository.save(otp)
    
    # 2. Mark as sent
    saved_otp.mark_as_sent()
    await otp_repository.update(saved_otp)
    
    # 3. Failed attempts
    for _ in range(2):
        saved_otp.increment_attempts()
        await otp_repository.update(saved_otp)
    
    # 4. Successful validation
    assert not saved_otp.has_exceeded_max_attempts()
    saved_otp.increment_attempts()  # Last attempt
    saved_otp.mark_as_validated()
    final_otp = await otp_repository.update(saved_otp)
    
    # Verify final state
    assert final_otp.status == OTPStatus.VALIDATED
    assert final_otp.attempts == 3
    assert final_otp.validated_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
