"""AccessControl entity - controla acceso a aplicaciones/módulos."""
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional


class AccessControl:
    """
    Entidad AccessControl - representa acceso a una aplicación/módulo por grupo.
    Basada en el modelo Django access del monolito.
    """
    
    def __init__(
        self,
        app_id: UUID,
        module_id: UUID,
        group_id: int,
        access_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = access_id or uuid4()
        self._app_id = app_id
        self._module_id = module_id
        self._group_id = group_id
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def app_id(self) -> UUID:
        return self._app_id
    
    @property
    def module_id(self) -> UUID:
        return self._module_id
    
    @property
    def group_id(self) -> int:
        return self._group_id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccessControl):
            return NotImplemented
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"AccessControl(id={self._id}, app={self._app_id}, module={self._module_id}, group={self._group_id})"
