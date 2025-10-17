"""SQLAlchemy repository adapters - implementan los puertos."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....core.ports import UserRepositoryPort
from ....core.domain.entity import User
from .models import UserModel


class SQLAlchemyUserRepository(UserRepositoryPort):
    """Adaptador: implementa UserRepositoryPort con SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _map_model_to_entity(self, model: UserModel) -> User:
        """Mapea UserModel (ORM) a User (domain entity)."""
        return User(
            user_id=model.id,
            username=model.username,
            email=model.email,
            name=model.name,
            last_name=model.last_name,
            is_active=model.is_active,
            is_staff=model.is_staff,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _map_entity_to_model(self, entity: User) -> UserModel:
        """Mapea User (domain entity) a UserModel (ORM)."""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            name=entity.name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            is_staff=entity.is_staff,
            is_superuser=entity.is_superuser,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    async def save(self, user: User) -> User:
        """Guarda (insert) un nuevo usuario."""
        model = self._map_entity_to_model(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._map_model_to_entity(model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene usuario por ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene usuario por username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene usuario por email."""
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def list_all(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Lista usuarios con paginación."""
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_model_to_entity(m) for m in models]
    
    async def update(self, user: User) -> User:
        """Actualiza un usuario existente."""
        model = await self.get_by_id(user.id)
        if not model:
            raise ValueError(f"Usuario con ID {user.id} no encontrado.")
        
        # Actualiza campos
        model_upd = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            name=user.name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        
        # Merge en la sesión
        await self.session.merge(model_upd)
        await self.session.commit()
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """Elimina un usuario."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
