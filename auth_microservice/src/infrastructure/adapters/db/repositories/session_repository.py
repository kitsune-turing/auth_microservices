"""Session Repository Implementation."""
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.ports.repository_ports import SessionRepositoryPort
from src.core.domain.entity import Session
from src.infrastructure.adapters.db.models.session_model import SessionModel

logger = logging.getLogger(__name__)


class SessionRepository(SessionRepositoryPort):
    """Repository for managing user sessions in the database."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def save(self, session_entity: Session) -> Session:
        """
        Save a session to the database.
        
        Args:
            session_entity: Session entity to save
            
        Returns:
            Saved Session entity
        """
        try:
            # Check if session already exists
            stmt = select(SessionModel).where(SessionModel.id == session_entity.id)
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing session
                existing.last_activity = session_entity.last_activity
                existing.expires_at = session_entity.expires_at
                existing.active = session_entity.active
                if not session_entity.active:
                    existing.ended_at = datetime.now(timezone.utc)
                logger.info(f"Updated session {session_entity.id} in database")
            else:
                # Create new session
                session_model = SessionModel(
                    id=session_entity.id,
                    user_id=session_entity.user_id,
                    access_token_id=session_entity.access_token_id,
                    ip_address=session_entity.ip_address,
                    user_agent=session_entity.user_agent,
                    created_at=session_entity.created_at,
                    last_activity=session_entity.last_activity,
                    expires_at=session_entity.expires_at,
                    active=session_entity.active,
                )
                self.session.add(session_model)
                logger.info(f"Created new session {session_entity.id} in database")
            
            await self.session.commit()
            return session_entity
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving session to database: {e}")
            raise
    
    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """
        Retrieve a session by its ID.
        
        Args:
            session_id: UUID of the session
            
        Returns:
            Session entity if found, None otherwise
        """
        try:
            stmt = select(SessionModel).where(SessionModel.id == session_id)
            result = await self.session.execute(stmt)
            session_model = result.scalar_one_or_none()
            
            if not session_model:
                return None
            
            return self._model_to_entity(session_model)
            
        except Exception as e:
            logger.error(f"Error retrieving session by ID: {e}")
            raise
    
    async def get_active_sessions_for_user(self, user_id: UUID) -> list[Session]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of active Session entities
        """
        try:
            stmt = select(SessionModel).where(
                SessionModel.user_id == user_id,
                SessionModel.active == True,
            ).order_by(SessionModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            session_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in session_models]
            
        except Exception as e:
            logger.error(f"Error retrieving active sessions: {e}")
            raise
    
    async def end_session(self, session_id: UUID) -> bool:
        """
        End a specific session.
        
        Args:
            session_id: UUID of the session to end
            
        Returns:
            True if session was ended, False if not found
        """
        try:
            stmt = (
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(active=False, ended_at=datetime.now(timezone.utc))
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Ended session {session_id}")
                return True
            
            logger.warning(f"Session {session_id} not found")
            return False
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error ending session: {e}")
            raise
    
    async def end_all_user_sessions(self, user_id: UUID) -> int:
        """
        End all sessions for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Number of sessions ended
        """
        try:
            stmt = (
                update(SessionModel)
                .where(
                    SessionModel.user_id == user_id,
                    SessionModel.active == True,
                )
                .values(active=False, ended_at=datetime.now(timezone.utc))
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            count = result.rowcount
            logger.info(f"Ended {count} sessions for user {user_id}")
            return count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error ending user sessions: {e}")
            raise
    
    def _model_to_entity(self, model: SessionModel) -> Session:
        """
        Convert ORM model to domain entity.
        
        Args:
            model: SessionModel ORM instance
            
        Returns:
            Session domain entity
        """
        return Session(
            session_id=model.id,
            user_id=model.user_id,
            access_token_id=model.access_token_id,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            created_at=model.created_at,
            last_activity=model.last_activity,
            expires_at=model.expires_at,
            active=model.active,
        )
