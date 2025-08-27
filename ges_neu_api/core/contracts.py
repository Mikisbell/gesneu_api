"""
Módulo de contratos para la API de Gestión de Neumáticos.

Este módulo define las interfaces (Protocols) que deben implementar los servicios
de la aplicación para garantizar la consistencia y facilitar el testing.
"""
from typing import Protocol, TypeVar, runtime_checkable, Any, Optional, List, Dict, Type
from typing_extensions import Self
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Tipos genéricos
T = TypeVar('T', bound=BaseModel)
ID = TypeVar('ID', int, str, bytes)

@runtime_checkable
class ServiceContract(Protocol[T]):
    """Interfaz base para todos los servicios de la aplicación."""
    
    @classmethod
    def create(cls, db: Session, *args: Any, **kwargs: Any) -> Self:
        """Crea una nueva instancia del servicio."""
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
class AuthServiceContract(ServiceContract, Protocol):
    """Contrato para el servicio de autenticación."""
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica un usuario con email y contraseña."""
        ...
    
    def get_current_user(self, token: str) -> Dict[str, Any]:
        """Obtiene el usuario actual a partir de un token JWT."""
        ...
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Crea un nuevo token de acceso JWT."""
        ...

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

def validate_implementation(implementation: object, contract: Type[Protocol]) -> bool:
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
