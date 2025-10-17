"""AccessControl repository adapter."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....core.ports import AccessControlRepositoryPort
from ....core.domain.entity import AccessControl
from .models import AccessControlModel


class SQLAlchemyAccessControlRepository(AccessControlRepositoryPort):
    """Adaptador: implementa AccessControlRepositoryPort con SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _map_model_to_entity(self, model: AccessControlModel) -> AccessControl:
        """Mapea AccessControlModel (ORM) a AccessControl (domain entity)."""
        return AccessControl(
            access_id=model.id,
            app_id=model.app_id,
            module_id=model.module_id,
            group_id=model.group_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _map_entity_to_model(self, entity: AccessControl) -> AccessControlModel:
        """Mapea AccessControl (domain entity) a AccessControlModel (ORM)."""
        return AccessControlModel(
            id=entity.id,
            app_id=entity.app_id,
            module_id=entity.module_id,
            group_id=entity.group_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    async def save(self, access: AccessControl) -> AccessControl:
        """Guarda un control de acceso."""
        model = self._map_entity_to_model(access)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._map_model_to_entity(model)
    
    async def get_by_id(self, access_id: UUID) -> Optional[AccessControl]:
        """Obtiene acceso por ID."""
        stmt = select(AccessControlModel).where(AccessControlModel.id == access_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def get_by_app_module_group(
        self, app_id: UUID, module_id: UUID, group_id: int
    ) -> Optional[AccessControl]:
        """Obtiene acceso por app, módulo y grupo."""
        stmt = select(AccessControlModel).where(
            (AccessControlModel.app_id == app_id)
            & (AccessControlModel.module_id == module_id)
            & (AccessControlModel.group_id == group_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def list_by_group(self, group_id: int) -> List[AccessControl]:
        """Lista accesos por grupo."""
        stmt = select(AccessControlModel).where(AccessControlModel.group_id == group_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_model_to_entity(m) for m in models]
    
    async def delete(self, access_id: UUID) -> bool:
        """Elimina un control de acceso."""
        stmt = select(AccessControlModel).where(AccessControlModel.id == access_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
