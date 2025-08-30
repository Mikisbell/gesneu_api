"""
Módulo de contratos para la API de Gestión de Neumáticos.

Este módulo define las interfaces (Protocols) que deben implementar los servicios
de la aplicación para garantizar la consistencia y facilitar el testing.
"""
from typing import Protocol, TypeVar, runtime_checkable, Any, Optional, List, Dict, Type
from typing_extensions import Self
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from uuid import UUID
# Removed direct imports of Usuario, UsuarioRead, etc.

# Tipos genéricos
T = TypeVar('T', bound=BaseModel)
ID = TypeVar('ID', int, str, bytes)

@runtime_checkable
class ServiceContract(Protocol[T]):
    """Interfaz base para todos los servicios de la aplicación."""
    

# ... (rest of the file) ...

@runtime_checkable
class UserServiceContract(Protocol):
    """Contrato para el servicio de usuarios."""
    
    async def get_user_by_id(self, user_id: UUID) -> Optional["UsuarioRead"]:
        """Obtiene un usuario por su ID."""
        ...
    
    async def get_user_by_username(self, username: str) -> Optional["UsuarioRead"]:
        """Obtiene un usuario por su nombre de usuario."""
        ...
    
    async def create_user(self, user_data: "UsuarioCreate") -> "UsuarioRead":
        """Crea un nuevo usuario."""
        ...
    
    async def update_user(self, user_id: UUID, user_data: "UsuarioUpdate") -> Optional["UsuarioRead"]:
        """Actualiza un usuario existente."""
        ...
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Elimina (desactiva) un usuario por su ID."""
        ...

@runtime_checkable
class CRUDServiceContract(ServiceContract[T], Protocol[T]):
    """Interfaz para servicios que implementan operaciones CRUD básicas."""
    
    def get(self, id: ID) -> Optional[T]:
        """Obtiene un elemento por su ID."""
        ...
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        """Obtiene múltiples elementos con paginación y filtros opcionales."""
        ...
    
    def create(self, obj_in: T) -> T:
        """Crea un nuevo elemento."""
        ...
    
    def update(self, id: ID, obj_in: T) -> Optional[T]:
        """Actualiza un elemento existente."""
        ...
    
    def delete(self, id: ID) -> bool:
        """Elimina un elemento por su ID.
        
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        ...

# Contratos específicos de módulos
@runtime_checkable
class AuthServiceContract(Protocol):
    """Contrato para el servicio de autenticación."""
    
    async def authenticate_user(self, username: str, password: str) -> Optional["Usuario"]:
        """Autentica un usuario con nombre de usuario y contraseña."""
        ...
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crea un nuevo token de acceso JWT."""
        ...
    
    async def get_current_user(self, token: str) -> "UsuarioRead":
        """Obtiene el usuario actual a partir de un token JWT."""
        ...

@runtime_checkable
class UserServiceContract(CRUDServiceContract[T], Protocol[T]):
    """Contrato para el servicio de usuarios."""
    pass

@runtime_checkable
class CatalogServiceContract(CRUDServiceContract[T], Protocol[T]):
    """Contrato para servicios de catálogos."""
    
    def search(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """Busca elementos que coincidan con la consulta."""
        ...

@runtime_checkable
class VehiculosServiceContract(CRUDServiceContract[T], Protocol[T]):
    """Contrato para servicios de vehículos."""
    pass

def validate_implementation(implementation: object, contract: Type[Any]) -> bool:
    """Valida que una implementación cumpla con un contrato.
    
    Args:
        implementation: La implementación a validar
        contract: El contrato (Protocol) que debe implementar
        
    Returns:
        bool: True si la implementación cumple con el contrato, False en caso contrario
    """
    if not isinstance(implementation, contract):
        required_methods = {
            name: method 
            for name, method in contract.__dict__.items()
            if callable(method) and not name.startswith('__')
        }
        
        missing_methods = [
            name for name in required_methods 
            if not hasattr(implementation, name) or not callable(getattr(implementation, name))
        ]
        
        if missing_methods:
            raise TypeError(
                f"La implementación no cumple con el contrato {contract.__name__}. "
                f"Métodos faltantes: {', '.join(missing_methods)}"
            )
    
    return True
