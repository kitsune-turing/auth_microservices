"""Logout Use Case.

Handles user logout by revoking tokens and ending sessions.
"""
import logging
from uuid import UUID

from src.core.ports.repository_ports import AuthTokenRepositoryPort, SessionRepositoryPort
from src.domain.value_objects import TokenPayload

logger = logging.getLogger(__name__)


class LogoutUseCase:
    """Use case for logging out users."""
    
    def __init__(
        self,
        token_repository: AuthTokenRepositoryPort,
        session_repository: SessionRepositoryPort,
    ):
        """
        Initialize logout use case.
        
        Args:
            token_repository: Token repository for revoking tokens
            session_repository: Session repository for ending sessions
        """
        self.token_repository = token_repository
        self.session_repository = session_repository
    
    async def execute(self, current_user: TokenPayload, access_token_string: str) -> dict:
        """
        Execute logout use case.
        
        Revokes the current access token and ends active sessions.
        
        Args:
            current_user: Current user from token payload
            access_token_string: The access token string to revoke
            
        Returns:
            Dict with logout confirmation
        """
        user_id_uuid = UUID(current_user.sub)
        logger.info(f"Logout request for user: {current_user.username} ({user_id_uuid})")
        
        # Step 1: Find and revoke the access token
        token_entity = await self.token_repository.get_by_token_string(access_token_string)
        if token_entity:
            await self.token_repository.revoke_token(token_entity.id)
            logger.info(f"Access token revoked: {token_entity.id}")
            
            # Step 2: End any sessions associated with this token
            sessions = await self.session_repository.get_active_sessions_for_user(user_id_uuid)
            for session in sessions:
                if session.access_token_id == token_entity.id:
                    await self.session_repository.end_session(session.id)
                    logger.info(f"Session ended: {session.id}")
        else:
            logger.warning(f"Token not found in database for user: {current_user.username}")
        
        logger.info(f"User logged out successfully: {current_user.username}")
        
        return {
            "message": "Logged out successfully",
            "user_id": current_user.sub,
            "username": current_user.username,
        }


__all__ = ["LogoutUseCase"]
