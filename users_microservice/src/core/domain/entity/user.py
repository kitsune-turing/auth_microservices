"""User entity - lógica de negocio pura sin dependencias externas."""
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, Set
from ..exceptions import InvalidEmailError, InvalidPasswordError


class User:
    """
    Entidad User - contiene lógica de negocio pura (sin BD, sin HTTP).
    Basada en el modelo Django User del monolito.
    """
    
    def __init__(
        self,
        username: str,
        email: str,
        name: str,
        last_name: str,
        user_id: Optional[UUID] = None,
        is_active: bool = True,
        is_staff: bool = False,
        is_superuser: bool = False,
        roles: Optional[Set[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        if not username or not username.strip():
            raise InvalidEmailError("Username no puede estar vacío.")
        if not email or not email.strip():
            raise InvalidEmailError("Email no puede estar vacío.")
        if not name or not name.strip():
            raise InvalidPasswordError("Name no puede estar vacío.")
        
        self._id = user_id or uuid4()
        self._username = username.strip()
        self._email = email.strip().lower()
        self._name = name.strip()
        self._last_name = last_name.strip()
        self._is_active = is_active
        self._is_staff = is_staff
        self._is_superuser = is_superuser
        self._roles = roles or set()
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)
    
    # Propiedades
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def last_name(self) -> str:
        return self._last_name
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def is_staff(self) -> bool:
        return self._is_staff
    
    @property
    def is_superuser(self) -> bool:
        return self._is_superuser
    
    @property
    def roles(self) -> Set[str]:
        return self._roles.copy()
    
    @property
    def full_name(self) -> str:
        return f"{self._name} {self._last_name}"
    
    # Métodos de negocio
    def activate(self) -> None:
        """Activa el usuario."""
        self._is_active = True
        self._updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Desactiva el usuario."""
        self._is_active = False
        self._updated_at = datetime.now(timezone.utc)
    
    def add_role(self, role: str) -> None:
        """Añade un rol."""
        self._roles.add(role)
        self._updated_at = datetime.now(timezone.utc)
    
    def remove_role(self, role: str) -> None:
        """Remueve un rol."""
        self._roles.discard(role)
        self._updated_at = datetime.now(timezone.utc)
    
    def has_role(self, role: str) -> bool:
        """Verifica si tiene un rol."""
        return role in self._roles
    
    def update_profile(self, name: Optional[str] = None, last_name: Optional[str] = None) -> None:
        """Actualiza perfil."""
        if name:
            self._name = name.strip()
        if last_name:
            self._last_name = last_name.strip()
        self._updated_at = datetime.now(timezone.utc)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"User(id={self._id}, username={self._username}, email={self._email})"