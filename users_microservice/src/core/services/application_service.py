"""Application service - casos de uso para aplicaciones."""
from typing import List, Optional
from uuid import UUID
from ..ports import ApplicationRepositoryPort
from ..domain.entity import Application
from ..domain.exceptions import ApplicationNotFoundError, ApplicationAlreadyExistsError


class CreateApplicationService:
    """Use case: crear aplicación."""
    
    def __init__(self, app_repo: ApplicationRepositoryPort):
        self.app_repo = app_repo
    
    async def execute(
        self,
        name: str,
        url: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Application:
        """Crea una nueva aplicación."""
        # Verifica que no exista ya
        existing = await self.app_repo.get_by_name(name)
        if existing:
            raise ApplicationAlreadyExistsError(f"Aplicación '{name}' ya existe.")
        
        app = Application(name=name, url=url, description=description)
        return await self.app_repo.save(app)


class GetApplicationService:
    """Use case: obtener aplicación."""
    
    def __init__(self, app_repo: ApplicationRepositoryPort):
        self.app_repo = app_repo
    
    async def execute(self, app_id: UUID) -> Application:
        """Obtiene aplicación por ID."""
        app = await self.app_repo.get_by_id(app_id)
        if not app:
            raise ApplicationNotFoundError(f"Aplicación con ID {app_id} no encontrada.")
        return app


class ListApplicationsService:
    """Use case: listar aplicaciones."""
    
    def __init__(self, app_repo: ApplicationRepositoryPort):
        self.app_repo = app_repo
    
    async def execute(self, skip: int = 0, limit: int = 10) -> List[Application]:
        """Lista aplicaciones."""
        return await self.app_repo.list_all(skip=skip, limit=limit)


class UpdateApplicationService:
    """Use case: actualizar aplicación."""
    
    def __init__(self, app_repo: ApplicationRepositoryPort):
        self.app_repo = app_repo
    
    async def execute(
        self,
        app_id: UUID,
        name: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Application:
        """Actualiza una aplicación."""
        app = await self.app_repo.get_by_id(app_id)
        if not app:
            raise ApplicationNotFoundError(f"Aplicación con ID {app_id} no encontrada.")
        
        app.update(name=name, url=url, description=description)
        return await self.app_repo.update(app)


class DeleteApplicationService:
    """Use case: eliminar aplicación."""
    
    def __init__(self, app_repo: ApplicationRepositoryPort):
        self.app_repo = app_repo
    
    async def execute(self, app_id: UUID) -> bool:
        """Elimina una aplicación."""
        app = await self.app_repo.get_by_id(app_id)
        if not app:
            raise ApplicationNotFoundError(f"Aplicación con ID {app_id} no encontrada.")
        
        return await self.app_repo.delete(app_id)
