"""JANO Service Port.

Port interface for JANO security validation service.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class JANOServicePort(ABC):
    """Port interface for JANO security service."""
    
    @abstractmethod
    async def validate_password(self, password: str) -> Dict[str, Any]:
        """
        Validate password against JANO password policies.
        
        Args:
            password: Password to validate
            
        Returns:
            Validation result with is_valid, violations, warnings
        """
        pass
    
    @abstractmethod
    async def validate_request(
        self,
        user_id: str,
        role: str,
        endpoint: str,
        method: str,
        ip_address: str,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate request against JANO security rules.
        
        Args:
            user_id: User ID making the request
            role: User role
            endpoint: Endpoint being accessed
            method: HTTP method
            ip_address: Client IP address
            user_agent: User agent string
            
        Returns:
            Validation result with should_block, violations, warnings
        """
        pass
    
    @abstractmethod
    async def validate_session(
        self,
        user_id: str,
        role: str,
        session_created_at: str,
        last_activity_at: str,
    ) -> Dict[str, Any]:
        """
        Validate session against JANO session policies.
        
        Args:
            user_id: User ID
            role: User role
            session_created_at: When session was created (ISO format)
            last_activity_at: Last activity timestamp (ISO format)
            
        Returns:
            Validation result with is_valid, violations
        """
        pass
    
    @abstractmethod
    async def validate_mfa_requirement(
        self,
        user_id: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Check if MFA is required for user.
        
        Args:
            user_id: User ID
            role: User role
            
        Returns:
            Validation result with mfa_required boolean
        """
        pass
