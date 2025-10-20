"""OTP Repository Implementation.

Database adapter implementing OTPRepositoryPort.
"""
import logging
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.ports import OTPRepositoryPort
from src.core.domain.entity import OTP, DeliveryMethod, OTPStatus
from .models import OTPModel, DeliveryMethodEnum, OTPStatusEnum

logger = logging.getLogger(__name__)


class OTPRepository(OTPRepositoryPort):
    """SQLAlchemy implementation of OTP repository."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository.
        
        Args:
            session: Database session
        """
        self.session = session
    
    def _model_to_entity(self, model: OTPModel) -> OTP:
        """
        Convert SQLAlchemy model to domain entity.
        
        Args:
            model: OTP model
            
        Returns:
            OTP domain entity
        """
        return OTP(
            otp_id=model.id,
            user_id=str(model.user_id),
            code=model.code,
            delivery_method=DeliveryMethod(model.delivery_method.value),
            recipient=model.recipient,
            expires_in_minutes=(model.expires_at - model.created_at).total_seconds() // 60,
            max_attempts=model.max_attempts,
            status=OTPStatus(model.status.value),
            created_at=model.created_at,
            attempts=model.attempts,
        )
    
    def _entity_to_model(self, entity: OTP) -> OTPModel:
        """
        Convert domain entity to SQLAlchemy model.
        
        Args:
            entity: OTP domain entity
            
        Returns:
            OTP model
        """
        model = OTPModel(
            id=entity.otp_id,
            user_id=UUID(entity.user_id),
            code=entity.code,
            delivery_method=DeliveryMethodEnum(entity.delivery_method.value),
            recipient=entity.recipient,
            status=OTPStatusEnum(entity.status.value),
            attempts=entity.attempts,
            max_attempts=entity.max_attempts,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            validated_at=entity.validated_at,
        )
        return model
    
    async def save(self, otp: OTP) -> OTP:
        """
        Save OTP to database.
        
        Args:
            otp: OTP entity to save
            
        Returns:
            Saved OTP entity
        """
        # Raw SQL insert into otp_codes table
        query = text("""
            INSERT INTO siata_auth.otp_codes 
            (otp_id, user_id, otp_code_hash, delivery_method, recipient, status, attempts, max_attempts, created_at, expires_at, validated_at)
            VALUES (:otp_id, :user_id, :otp_code_hash, :delivery_method, :recipient, :status, :attempts, :max_attempts, :created_at, :expires_at, :validated_at)
            RETURNING otp_id, user_id, otp_code_hash, delivery_method, recipient, status, attempts, max_attempts, created_at, expires_at, validated_at
        """)
        
        await self.session.execute(query, {
            "otp_id": otp.otp_id,
            "user_id": UUID(otp.user_id),
            "otp_code_hash": otp.code,  # The code is stored as hash
            "delivery_method": otp.delivery_method.value,
            "recipient": otp.recipient,
            "status": otp.status.value,
            "attempts": otp.attempts,
            "max_attempts": otp.max_attempts,
            "created_at": otp.created_at,
            "expires_at": otp.expires_at,
            "validated_at": otp.validated_at,
        })
        
        await self.session.commit()
        
        logger.info(f"OTP saved to database: {otp.otp_id}")
        return otp
    
    async def get_by_id(self, otp_id: UUID) -> Optional[OTP]:
        """
        Get OTP by ID.
        
        Args:
            otp_id: OTP identifier
            
        Returns:
            OTP entity if found, None otherwise
        """
        query = text("""
            SELECT otp_id, user_id, otp_code_hash, delivery_method, recipient, status, 
                   attempts, max_attempts, created_at, expires_at, validated_at
            FROM siata_auth.otp_codes
            WHERE otp_id = :otp_id
        """)
        
        result = await self.session.execute(query, {"otp_id": otp_id})
        row = result.first()
        
        if row:
            logger.debug(f"OTP found: {otp_id}")
            # Map database row to OTP entity
            otp = OTP(
                otp_id=row[0],
                user_id=str(row[1]),
                code=row[2],  # otp_code_hash
                delivery_method=DeliveryMethod(row[3]),  # delivery_method
                recipient=row[4],
                expires_in_minutes=5,  # Calculate from expires_at - created_at if needed
                max_attempts=row[7],  # max_attempts
                status=OTPStatus(row[5]),  # status
                created_at=row[8],  # created_at
                attempts=row[6],  # attempts
            )
            # Set validated_at separately since it's not in the constructor
            otp.validated_at = row[10]  # validated_at
            return otp
        
        logger.debug(f"OTP not found: {otp_id}")
        return None
    
    async def get_by_user_id(self, user_id: str) -> list[OTP]:
        """
        Get all OTPs for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of OTP entities
        """
        query = text("""
            SELECT otp_id, user_id, otp_code_hash, delivery_method, recipient, status,
                   attempts, max_attempts, created_at, expires_at, validated_at
            FROM siata_auth.otp_codes
            WHERE user_id = :user_id
        """)
        
        result = await self.session.execute(query, {"user_id": UUID(user_id)})
        rows = result.fetchall()
        
        logger.debug(f"Found {len(rows)} OTPs for user {user_id}")
        
        otps = []
        for row in rows:
            otp = OTP(
                otp_id=row[0],
                user_id=str(row[1]),
                code=row[2],  # otp_code_hash
                delivery_method=DeliveryMethod(row[3]),  # delivery_method
                recipient=row[4],
                expires_in_minutes=5,
                max_attempts=row[7],  # max_attempts
                status=OTPStatus(row[5]),  # status
                created_at=row[8],  # created_at
                attempts=row[6],  # attempts
            )
            # Set validated_at separately since it's not in the constructor
            otp.validated_at = row[10]  # validated_at
            otps.append(otp)
        
        return otps
    
    async def update(self, otp: OTP) -> OTP:
        """
        Update existing OTP.
        
        Args:
            otp: OTP entity to update
            
        Returns:
            Updated OTP entity
        """
        query = text("""
            UPDATE siata_auth.otp_codes
            SET otp_code_hash = :otp_code_hash, 
                status = :status, 
                attempts = :attempts, 
                validated_at = :validated_at
            WHERE otp_id = :otp_id
            RETURNING otp_id, user_id, otp_code_hash, delivery_method, recipient, status,
                      attempts, max_attempts, created_at, expires_at, validated_at
        """)
        
        result = await self.session.execute(query, {
            "otp_id": otp.otp_id,
            "otp_code_hash": otp.code,
            "status": otp.status.value,
            "attempts": otp.attempts,
            "validated_at": otp.validated_at,
        })
        
        await self.session.commit()
        row = result.first()
        
        if not row:
            raise ValueError(f"OTP not found: {otp.otp_id}")
        
        logger.info(f"OTP updated in database: {otp.otp_id}")
        return otp
    
    async def delete_expired(self) -> int:
        """
        Delete all expired OTPs.
        
        Returns:
            Number of deleted OTPs
        """
        now = datetime.now(UTC)
        query = text("""
            DELETE FROM siata_auth.otp_codes
            WHERE expires_at < :now
        """)
        
        result = await self.session.execute(query, {"now": now})
        await self.session.commit()
        
        deleted_count = result.rowcount
        logger.info(f"Deleted {deleted_count} expired OTPs")
        return deleted_count


__all__ = ["OTPRepository"]
