"""Authentication Token Repository Implementation."""
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.ports.repository_ports import AuthTokenRepositoryPort
from src.core.domain.entity import AuthToken, TokenType
from src.infrastructure.adapters.db.models.auth_token_model import AuthTokenModel

logger = logging.getLogger(__name__)


class AuthTokenRepository(AuthTokenRepositoryPort):
    """Repository for managing authentication tokens in the database."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def save(self, token: AuthToken) -> AuthToken:
        """
        Save an authentication token to the database.
        
        Args:
            token: AuthToken entity to save
            
        Returns:
            Saved AuthToken entity
        """
        try:
            # Check if token already exists
            stmt = select(AuthTokenModel).where(AuthTokenModel.id == token.id)
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing token
                existing.token_hash = token.token_hash
                existing.jti = token.jti
                existing.expires_at = token.expires_at
                existing.revoked = token.revoked
                if token.revoked:
                    existing.revoked_at = datetime.now(timezone.utc)
                logger.info(f"Updated token {token.id} in database")
            else:
                # Create new token
                token_model = AuthTokenModel(
                    id=token.id,
                    user_id=token.user_id,
                    token_type=token.token_type,
                    token_hash=token.token_hash,
                    jti=token.jti,
                    expires_at=token.expires_at,
                    created_at=token.created_at,
                    revoked=token.revoked,
                )
                self.session.add(token_model)
                logger.info(f"Created new token {token.id} in database")
            
            await self.session.commit()
            return token
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving token to database: {e}")
            raise
    
    async def get_by_id(self, token_id: UUID) -> Optional[AuthToken]:
        """
        Retrieve a token by its ID.
        
        Args:
            token_id: UUID of the token
            
        Returns:
            AuthToken entity if found, None otherwise
        """
        try:
            stmt = select(AuthTokenModel).where(AuthTokenModel.id == token_id)
            result = await self.session.execute(stmt)
            token_model = result.scalar_one_or_none()
            
            if not token_model:
                return None
            
            return self._model_to_entity(token_model)
            
        except Exception as e:
            logger.error(f"Error retrieving token by ID: {e}")
            raise
    
    async def get_by_token_hash(self, token_hash: str) -> Optional[AuthToken]:
        """
        Retrieve a token by its SHA-256 hash.
        
        Args:
            token_hash: SHA-256 hash of the JWT token (64 hex characters)
            
        Returns:
            AuthToken entity if found, None otherwise
        """
        try:
            stmt = select(AuthTokenModel).where(
                AuthTokenModel.token_hash == token_hash
            )
            result = await self.session.execute(stmt)
            token_model = result.scalar_one_or_none()
            
            if not token_model:
                logger.debug("Token hash not found in database")
                return None
            
            return self._model_to_entity(token_model)
            
        except Exception as e:
            logger.error(f"Error retrieving token by hash: {e}")
            raise
    
    async def get_by_jti(self, jti: UUID) -> Optional[AuthToken]:
        """
        Retrieve a token by its JWT ID (jti).
        
        Args:
            jti: JWT ID (UUID)
            
        Returns:
            AuthToken entity if found, None otherwise
        """
        try:
            stmt = select(AuthTokenModel).where(
                AuthTokenModel.jti == jti
            )
            result = await self.session.execute(stmt)
            token_model = result.scalar_one_or_none()
            
            if not token_model:
                logger.debug(f"Token with jti {jti} not found in database")
                return None
            
            return self._model_to_entity(token_model)
            
        except Exception as e:
            logger.error(f"Error retrieving token by jti: {e}")
            raise
    
    async def revoke_token(self, token_id: UUID) -> bool:
        """
        Revoke a specific token.
        
        Args:
            token_id: UUID of the token to revoke
            
        Returns:
            True if token was revoked, False if not found
        """
        try:
            stmt = (
                update(AuthTokenModel)
                .where(AuthTokenModel.id == token_id)
                .values(revoked=True, revoked_at=datetime.now(timezone.utc))
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Revoked token {token_id}")
                return True
            
            logger.warning(f"Token {token_id} not found for revocation")
            return False
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error revoking token: {e}")
            raise
    
    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """
        Revoke all tokens for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Number of tokens revoked
        """
        try:
            stmt = (
                update(AuthTokenModel)
                .where(
                    AuthTokenModel.user_id == user_id,
                    AuthTokenModel.revoked == False,
                )
                .values(revoked=True, revoked_at=datetime.now(timezone.utc))
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            count = result.rowcount
            logger.info(f"Revoked {count} tokens for user {user_id}")
            return count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error revoking user tokens: {e}")
            raise
    
    def _model_to_entity(self, model: AuthTokenModel) -> AuthToken:
        """
        Convert ORM model to domain entity.
        
        Args:
            model: AuthTokenModel ORM instance
            
        Returns:
            AuthToken domain entity
        """
        return AuthToken(
            token_id=model.id,
            user_id=model.user_id,
            token_type=model.token_type,
            token_hash=model.token_hash,
            jti=model.jti,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked=model.revoked,
        )
