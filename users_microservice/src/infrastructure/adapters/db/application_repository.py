"""Application repository adapter."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....core.ports import ApplicationRepositoryPort
from ....core.domain.entity import Application
from .models import ApplicationModel


class SQLAlchemyApplicationRepository(ApplicationRepositoryPort):
    """Adaptador: implementa ApplicationRepositoryPort con SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _map_model_to_entity(self, model: ApplicationModel) -> Application:
        """Mapea ApplicationModel (ORM) a Application (domain entity)."""
        return Application(
            app_id=model.id,
            name=model.name,
            url=model.url,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _map_entity_to_model(self, entity: Application) -> ApplicationModel:
        """Mapea Application (domain entity) a ApplicationModel (ORM)."""
        return ApplicationModel(
            id=entity.id,
            name=entity.name,
            url=entity.url,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    async def save(self, application: Application) -> Application:
        """Guarda una aplicación."""
        model = self._map_entity_to_model(application)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._map_model_to_entity(model)
    
    async def get_by_id(self, app_id: UUID) -> Optional[Application]:
        """Obtiene aplicación por ID."""
        stmt = select(ApplicationModel).where(ApplicationModel.id == app_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def get_by_name(self, name: str) -> Optional[Application]:
        """Obtiene aplicación por nombre."""
        stmt = select(ApplicationModel).where(ApplicationModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def list_all(self, skip: int = 0, limit: int = 10) -> List[Application]:
        """Lista aplicaciones."""
        stmt = select(ApplicationModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_model_to_entity(m) for m in models]
    
    async def update(self, application: Application) -> Application:
        """Actualiza una aplicación."""
        model_upd = self._map_entity_to_model(application)
        await self.session.merge(model_upd)
        await self.session.commit()
        return application
    
    async def delete(self, app_id: UUID) -> bool:
        """Elimina una aplicación."""
        stmt = select(ApplicationModel).where(ApplicationModel.id == app_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
