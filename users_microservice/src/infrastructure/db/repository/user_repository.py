"""User Repository implementation using SQLAlchemy.

This adapter implements the UserRepositoryPort interface.
"""
import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, update, text
from sqlalchemy.orm import aliased

from src.core.ports.repository_ports import UserRepositoryPort
from src.infrastructure.db.models import UserModel

logger = logging.getLogger(__name__)


class UserRepository(UserRepositoryPort):
    """SQLAlchemy implementation of UserRepository port."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        name: str,
        last_name: str,
        role: str,
        team_id: Optional[UUID] = None,
    ) -> UUID:
        """Create a new user and return the user ID."""
        try:
            user = UserModel(
                username=username,
                email=email,
                password_hash=password_hash,
                name=name,
                last_name=last_name,
                role=role,
                team_id=team_id,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            
            logger.info(f"User created: {username} (id={user.id}, role={role})")
            return user.id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[dict]:
        """Get user by ID. Returns dict with user data or None."""
        try:
            # Use raw SQL with explicit schema and LEFT JOIN for team name
            query = text("""
                SELECT u.user_id, u.username, u.email, u.password_hash, u.first_name, u.last_name, u.role, 
                       u.team_id, u.status, u.created_at, u.updated_at, t.team_name, u.is_mfa_enabled
                FROM siata_auth.users u
                LEFT JOIN siata_auth.teams t ON u.team_id = t.team_id
                WHERE u.user_id = :user_id
            """)
            result = await self.session.execute(query, {"user_id": str(user_id)})
            row = result.first()
            
            if row:
                return {
                    'id': UUID(str(row[0])),
                    'username': row[1],
                    'email': row[2],
                    'password_hash': row[3],
                    'name': row[4],
                    'last_name': row[5],
                    'role': row[6],
                    'team_id': row[7],
                    'status': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'team_name': row[11],
                    'is_mfa_enabled': row[12],
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username. Returns dict with user data or None."""
        try:
            # Use raw SQL with explicit schema and LEFT JOIN for team name
            query = text("""
                SELECT u.user_id, u.username, u.email, u.password_hash, u.first_name, u.last_name, u.role, 
                       u.team_id, u.status, u.created_at, u.updated_at, t.team_name, u.is_mfa_enabled
                FROM siata_auth.users u
                LEFT JOIN siata_auth.teams t ON u.team_id = t.team_id
                WHERE u.username = :username
            """)
            result = await self.session.execute(query, {"username": username})
            row = result.first()
            
            if row:
                return {
                    'id': UUID(str(row[0])),
                    'username': row[1],
                    'email': row[2],
                    'password_hash': row[3],
                    'name': row[4],
                    'last_name': row[5],
                    'role': row[6],
                    'team_id': row[7],
                    'status': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'team_name': row[11],
                    'is_mfa_enabled': row[12],
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by username: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email. Returns dict with user data (including password_hash) or None."""
        try:
            # Use raw SQL with explicit schema and LEFT JOIN for team name
            query = text("""
                SELECT u.user_id, u.username, u.email, u.password_hash, u.first_name, u.last_name, u.role, 
                       u.team_id, u.status, u.created_at, u.updated_at, t.team_name, u.is_mfa_enabled
                FROM siata_auth.users u
                LEFT JOIN siata_auth.teams t ON u.team_id = t.team_id
                WHERE u.email = :email
            """)
            result = await self.session.execute(query, {"email": email})
            row = result.first()
            
            if row:
                return {
                    'id': UUID(str(row[0])),
                    'username': row[1],
                    'email': row[2],
                    'password_hash': row[3],
                    'name': row[4],
                    'last_name': row[5],
                    'role': row[6],
                    'team_id': row[7],
                    'status': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'team_name': row[11],
                    'is_mfa_enabled': row[12],
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            raise
    
    async def update_user(
        self,
        user_id: UUID,
        email: Optional[str] = None,
        name: Optional[str] = None,
        last_name: Optional[str] = None,
        team_id: Optional[UUID] = None,
    ) -> Optional[dict]:
        """Update user data. Returns updated user dict or None if failed."""
        try:
            # Build update values dict
            update_values = {}
            if email is not None:
                update_values['email'] = email
            if name is not None:
                update_values['name'] = name
            if last_name is not None:
                update_values['last_name'] = last_name
            if team_id is not None:
                update_values['team_id'] = team_id
            
            if not update_values:
                return None  # Nothing to update
            
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(**update_values)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"User {user_id} updated")
                # Return the updated user
                return await self.get_user_by_id(user_id)
            return None
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update user: {str(e)}")
            raise
    
    async def update_password(self, user_id: UUID, password_hash: str) -> bool:
        """Update user password hash. Returns True if successful."""
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(password_hash=password_hash)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Password updated for user {user_id}")
                return True
            return False
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update password: {str(e)}")
            raise
    
    async def update_role(
        self,
        user_id: UUID,
        role: str,
        team_id: Optional[UUID] = None,
    ) -> bool:
        """Update user role and team. Returns True if successful."""
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(role=role, team_id=team_id)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Role updated for user {user_id}: {role}")
                return True
            return False
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update role: {str(e)}")
            raise
    
    async def disable_user(self, user_id: UUID) -> Optional[dict]:
        """Disable user (set status to inactive). Returns updated user dict or None."""
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(status='inactive')
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"User {user_id} disabled")
                # Return the updated user
                return await self.get_user_by_id(user_id)
            return None
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to disable user: {str(e)}")
            raise
    
    async def enable_user(self, user_id: UUID) -> Optional[dict]:
        """Enable user (set status to active). Returns updated user dict or None."""
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(status='active')
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"User {user_id} enabled")
                # Return the updated user
                return await self.get_user_by_id(user_id)
            return None
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to enable user: {str(e)}")
            raise
    
    async def list_users(
        self,
        page: int = 1,
        size: int = 10,
        role: Optional[str] = None,
        active_only: bool = False,
    ) -> tuple[List[dict], int]:
        """
        List users with pagination and filters.
        Returns tuple of (users_list, total_count).
        """
        try:
            # Build filters
            filters = []
            if role is not None:
                filters.append(UserModel.role == role)
            if active_only:
                filters.append(UserModel.status == 'active')
            
            # Count total
            count_stmt = select(func.count(UserModel.id))
            if filters:
                count_stmt = count_stmt.where(and_(*filters))
            
            count_result = await self.session.execute(count_stmt)
            total = count_result.scalar()
            
            # Get users with pagination
            offset = (page - 1) * size
            users_stmt = select(UserModel)
            if filters:
                users_stmt = users_stmt.where(and_(*filters))
            users_stmt = users_stmt.offset(offset).limit(size)
            
            users_result = await self.session.execute(users_stmt)
            users = users_result.scalars().all()
            
            users_list = [user.to_dict() for user in users]
            
            logger.info(f"Listed {len(users_list)} users (total={total}, page={page})")
            return users_list, total
            
        except Exception as e:
            logger.error(f"Failed to list users: {str(e)}")
            raise
    
    async def user_exists(self, username: str = None, email: str = None) -> bool:
        """Check if user exists by username or email."""
        try:
            if username:
                query = text("""
                    SELECT user_id FROM siata_auth.users WHERE username = :username LIMIT 1
                """)
                result = await self.session.execute(query, {"username": username})
            elif email:
                query = text("""
                    SELECT user_id FROM siata_auth.users WHERE email = :email LIMIT 1
                """)
                result = await self.session.execute(query, {"email": email})
            else:
                return False
            
            return result.first() is not None
            
        except Exception as e:
            logger.error(f"Failed to check user existence: {str(e)}")
            raise


__all__ = ["UserRepository"]
