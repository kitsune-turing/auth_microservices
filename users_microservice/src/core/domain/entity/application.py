"""Application entity - lógica de negocio pura."""
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from ..exceptions import ApplicationAlreadyExistsError


class Application:
    """
    Entidad Application - representa una aplicación del sistema.
    Basada en el modelo Django applications del monolito.
    """
    
    def __init__(
        self,
        name: str,
        url: Optional[str] = None,
        description: Optional[str] = None,
        app_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        if not name or not name.strip():
            raise ValueError("Application name no puede estar vacío.")
        
        self._id = app_id or uuid4()
        self._name = name.strip()
        self._url = url.strip() if url else None
        self._description = description.strip() if description else None
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def url(self) -> Optional[str]:
        return self._url
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def update(self, name: Optional[str] = None, url: Optional[str] = None, description: Optional[str] = None) -> None:
        """Actualiza la aplicación."""
        if name:
            self._name = name.strip()
        if url is not None:
            self._url = url.strip() if url else None
        if description is not None:
            self._description = description.strip() if description else None
        self._updated_at = datetime.now(timezone.utc)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Application):
            return NotImplemented
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"Application(id={self._id}, name={self._name})"
