"""OTP Repository Port.

Port interface for OTP persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.core.domain.entity import OTP


class OTPRepositoryPort(ABC):
    """Port interface for OTP repository."""
    
    @abstractmethod
    async def save(self, otp: OTP) -> OTP:
        """
        Save OTP to storage.
        
        Args:
            otp: OTP entity to save
            
        Returns:
            Saved OTP entity
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, otp_id: UUID) -> Optional[OTP]:
        """
        Get OTP by ID.
        
        Args:
            otp_id: OTP identifier
            
        Returns:
            OTP entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[OTP]:
        """
        Get all OTPs for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of OTP entities
        """
        pass
    
    @abstractmethod
    async def update(self, otp: OTP) -> OTP:
        """
        Update existing OTP.
        
        Args:
            otp: OTP entity to update
            
        Returns:
            Updated OTP entity
        """
        pass
    
    @abstractmethod
    async def delete_expired(self) -> int:
        """
        Delete all expired OTPs.
        
        Returns:
            Number of deleted OTPs
        """
        pass


__all__ = ["OTPRepositoryPort"]
