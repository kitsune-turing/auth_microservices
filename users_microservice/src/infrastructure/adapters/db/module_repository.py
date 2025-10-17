"""Module repository adapter."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....core.ports import ModuleRepositoryPort
from ....core.domain.entity import Module
from .models import ModuleModel


class SQLAlchemyModuleRepository(ModuleRepositoryPort):
    """Adaptador: implementa ModuleRepositoryPort con SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _map_model_to_entity(self, model: ModuleModel) -> Module:
        """Mapea ModuleModel (ORM) a Module (domain entity)."""
        return Module(
            module_id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _map_entity_to_model(self, entity: Module) -> ModuleModel:
        """Mapea Module (domain entity) a ModuleModel (ORM)."""
        return ModuleModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    async def save(self, module: Module) -> Module:
        """Guarda un módulo."""
        model = self._map_entity_to_model(module)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._map_model_to_entity(model)
    
    async def get_by_id(self, module_id: UUID) -> Optional[Module]:
        """Obtiene módulo por ID."""
        stmt = select(ModuleModel).where(ModuleModel.id == module_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def get_by_name(self, name: str) -> Optional[Module]:
        """Obtiene módulo por nombre."""
        stmt = select(ModuleModel).where(ModuleModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._map_model_to_entity(model) if model else None
    
    async def list_all(self, skip: int = 0, limit: int = 10) -> List[Module]:
        """Lista módulos."""
        stmt = select(ModuleModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_model_to_entity(m) for m in models]
    
    async def update(self, module: Module) -> Module:
        """Actualiza un módulo."""
        model_upd = self._map_entity_to_model(module)
        await self.session.merge(model_upd)
        await self.session.commit()
        return module
    
    async def delete(self, module_id: UUID) -> bool:
        """Elimina un módulo."""
        stmt = select(ModuleModel).where(ModuleModel.id == module_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
