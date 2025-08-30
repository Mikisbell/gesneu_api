"""
Módulo para manejar la autorización a nivel de objeto (BOLA - Broken Object Level Authorization).

Este módulo proporciona utilidades para verificar que un usuario tenga permisos
sobre un objeto específico antes de realizar operaciones sobre él.
"""
from typing import Any, Type, TypeVar, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .exceptions import UnauthorizedException

T = TypeVar('T')

class ObjectPermissionError(UnauthorizedException):
    """Excepción lanzada cuando un usuario no tiene permisos sobre un objeto."""
    def __init__(self, detail: str = "No tiene permisos para acceder a este recurso"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code="permission_denied"
        )

class ObjectPermissionChecker:
    """
    Clase base para verificar permisos a nivel de objeto.
    
    Esta clase debe ser heredada para implementar la lógica específica de
    verificación de permisos para cada tipo de recurso.
    """
    
    @classmethod
    async def check_permission(
        cls,
        db: AsyncSession,
        user_id: UUID,
        object_id: UUID,
        action: str = "read"
    ) -> bool:
        """
        Verifica si un usuario tiene permiso para realizar una acción sobre un objeto.
        
        Args:
            db: Sesión de base de datos asíncrona
            user_id: ID del usuario que realiza la acción
            object_id: ID del objeto sobre el que se quiere actuar
            action: Acción que se quiere realizar (read, update, delete, etc.)
            
        Returns:
            bool: True si el usuario tiene permiso, False en caso contrario
            
        Raises:
            ObjectPermissionError: Si el usuario no tiene permiso
        """
        # Este método debe ser implementado por las subclases
        raise NotImplementedError("El método check_permission debe ser implementado por las subclases")
    
    @classmethod
    async def get_object_or_404(
        cls,
        db: AsyncSession,
        model: Type[T],
        object_id: UUID,
        user_id: Optional[UUID] = None,
        action: str = "read"
    ) -> T:
        """
        Obtiene un objeto de la base de datos o lanza una excepción 404 si no existe.
        
        Si se proporciona un user_id, también verifica los permisos sobre el objeto.
        
        Args:
            db: Sesión de base de datos asíncrona
            model: Clase del modelo SQLAlchemy
            object_id: ID del objeto a obtener
            user_id: ID del usuario que realiza la acción (opcional)
            action: Acción que se quiere realizar (read, update, delete, etc.)
            
        Returns:
            El objeto solicitado si existe y el usuario tiene permisos
            
        Raises:
            HTTPException 404: Si el objeto no existe
            ObjectPermissionError: Si el usuario no tiene permisos sobre el objeto
        """
        # Obtener el objeto
        result = await db.execute(select(model).where(model.id == object_id))
        obj = result.scalars().first()
        
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recurso con ID {object_id} no encontrado"
            )
        
        # Verificar permisos si se proporcionó un user_id
        if user_id is not None and hasattr(obj, 'owner_id'):
            if str(obj.owner_id) != str(user_id):
                raise ObjectPermissionError()
        
        return obj

# Ejemplo de implementación para un servicio específico
class CatalogItemPermissionChecker(ObjectPermissionChecker):
    """Verificador de permisos para ítems del catálogo."""
    
    @classmethod
    async def check_permission(
        cls,
        db: AsyncSession,
        user_id: UUID,
        object_id: UUID,
        action: str = "read"
    ) -> bool:
        """
        Verifica si un usuario puede realizar una acción sobre un ítem del catálogo.
        
        Los administradores pueden hacer cualquier acción.
        Los usuarios solo pueden leer/editar/eliminar sus propios ítems.
        """
        from ..auth.service import UserService
        from ..auth.models.usuario import Usuario
        
        # Obtener el usuario
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        # Si el usuario no existe o está inactivo, no tiene permisos
        if not user or not user.activo:
            return False
            
        # Los administradores tienen acceso completo
        if user.is_admin:
            return True
            
        # Obtener el ítem del catálogo
        from ..catalogos.models import CatalogoItem
        result = await db.execute(
            select(CatalogoItem)
            .where(CatalogoItem.id == object_id)
        )
        item = result.scalars().first()
        
        # Si el ítem no existe, no hay permisos que verificar
        if not item:
            return False
            
        # El propietario puede realizar cualquier acción
        return str(item.owner_id) == str(user_id)
