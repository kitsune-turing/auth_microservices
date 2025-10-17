"""User service - casos de uso para usuarios."""
from typing import List, Optional
from uuid import UUID
from ..ports import UserRepositoryPort
from ..domain.entity import User
from ..domain.exceptions import UserNotFoundError, UserAlreadyExistsError


class CreateUserService:
    """Use case: crear usuario."""
    
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def execute(
        self,
        username: str,
        email: str,
        name: str,
        last_name: str,
        is_active: bool = True,
    ) -> User:
        """Crea un nuevo usuario."""
        # Verifica que no exista ya
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(f"Email '{email}' ya está en uso.")
        
        existing_user = await self.user_repo.get_by_username(username)
        if existing_user:
            raise UserAlreadyExistsError(f"Username '{username}' ya está en uso.")
        
        # Crea la entidad
        user = User(
            username=username,
            email=email,
            name=name,
            last_name=last_name,
            is_active=is_active,
        )
        
        # Persiste
        return await self.user_repo.save(user)


class GetUserService:
    """Use case: obtener usuario por ID."""
    
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def execute(self, user_id: UUID) -> User:
        """Obtiene usuario por ID."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado.")
        return user


class ListUsersService:
    """Use case: listar usuarios."""
    
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def execute(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Lista usuarios con paginación."""
        return await self.user_repo.list_all(skip=skip, limit=limit)


class UpdateUserService:
    """Use case: actualizar usuario."""
    
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def execute(
        self,
        user_id: UUID,
        name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """Actualiza un usuario."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado.")
        
        user.update_profile(name=name, last_name=last_name)
        return await self.user_repo.update(user)


class DeleteUserService:
    """Use case: eliminar usuario."""
    
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def execute(self, user_id: UUID) -> bool:
        """Elimina un usuario."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado.")
        
        return await self.user_repo.delete(user_id)


class ActivateUserService:
    """Use case: activar usuario."""
    
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def execute(self, user_id: UUID) -> User:
        """Activa un usuario."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado.")
        
        user.activate()
        return await self.user_repo.update(user)


class DeactivateUserService:
    """Use case: desactivar usuario."""
    
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def execute(self, user_id: UUID) -> User:
        """Desactiva un usuario."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado.")
        
        user.deactivate()
        return await self.user_repo.update(user)
