"""
Pruebas unitarias para los servicios de autenticación.

Este módulo contiene pruebas para los servicios definidos en el módulo de autenticación.
"""
import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ges_neu_api.modules.auth import models, schemas, service
from ges_neu_api.core.exceptions import NotFoundException, BadRequestException

# Fixtures

@pytest.fixture
def mock_db_session():
    """Fixture que proporciona una sesión de base de datos simulada."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def auth_service(mock_db_session):
    """Fixture que proporciona una instancia de AuthService con una sesión simulada."""
    return service.AuthService(mock_db_session)

@pytest.fixture
def user_service(mock_db_session):
    """Fixture que proporciona una instancia de UserService con una sesión simulada."""
    return service.UserService(mock_db_session)

@pytest.fixture
def role_service(mock_db_session):
    """Fixture que proporciona una instancia de RoleService con una sesión simulada."""
    return service.RoleService(mock_db_session)

@pytest.fixture
def permission_service(mock_db_session):
    """Fixture que proporciona una instancia de PermissionService con una sesión simulada."""
    return service.PermissionService(mock_db_session)

# Tests para PermissionService

class TestPermissionService:
    """Pruebas para el servicio de permisos."""
    
    async def test_get_permission_by_id_found(self, permission_service, mock_db_session):
        """Prueba que se pueda obtener un permiso por su ID."""
        # Configurar el mock
        mock_permission = models.Permiso(
            id=uuid4(),
            nombre_recurso="recurso",
            accion="leer",
            descripcion="Permiso de lectura"
        )
        
        mock_db_session.get.return_value = mock_permission
        
        # Ejecutar
        result = await permission_service.get_permission_by_id(mock_permission.id)
        
        # Verificar
        assert result is not None
        assert result.id == mock_permission.id
        assert result.nombre_recurso == "recurso"
        assert result.accion == "leer"
        mock_db_session.get.assert_awaited_once_with(models.Permiso, str(mock_permission.id))
    
    async def test_get_permission_by_id_not_found(self, permission_service, mock_db_session):
        """Prueba que se maneje correctamente cuando no se encuentra un permiso."""
        # Configurar el mock
        mock_db_session.get.return_value = None
        
        # Ejecutar
        result = await permission_service.get_permission_by_id(uuid4())
        
        # Verificar
        assert result is None
    
    async def test_get_permission_by_resource_action_found(self, permission_service, mock_db_session):
        """Prueba que se pueda obtener un permiso por recurso y acción."""
        # Configurar el mock
        mock_permission = models.Permiso(
            id=uuid4(),
            nombre_recurso="recurso",
            accion="leer",
            descripcion="Permiso de lectura"
        )
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = mock_permission
        mock_db_session.execute.return_value = mock_result
        
        # Ejecutar
        result = await permission_service.get_permission_by_resource_action("recurso", "leer")
        
        # Verificar
        assert result is not None
        assert result.id == mock_permission.id
        assert result.nombre_recurso == "recurso"
        assert result.accion == "leer"
        
        # Verificar que se llamó a execute con la consulta correcta
        args, _ = mock_db_session.execute.call_args
        stmt = args[0]
        assert "WHERE" in str(stmt)
        assert "permisos.nombre_recurso" in str(stmt)
        assert "permisos.accion" in str(stmt)
    
    async def test_check_permission_superuser(self, permission_service, mock_db_session):
        """Prueba que un superusuario tenga todos los permisos."""
        # Configurar el mock para devolver un superusuario
        mock_user = models.Usuario(
            id=uuid4(),
            email="admin@example.com",
            es_superusuario=True
        )
        mock_db_session.get.return_value = mock_user
        
        # Ejecutar con un permiso cualquiera
        result = await permission_service.check_permission(
            user_id=mock_user.id,
            resource="cualquier_recurso",
            action="cualquier_accion"
        )
        
        # Verificar que devuelve True sin importar el permiso
        assert result is True
    
    async def test_check_permission_user_with_permission(self, permission_service, mock_db_session):
        """Prueba que un usuario con el permiso pueda acceder."""
        # Configurar el mock para el usuario (no superusuario)
        user_id = uuid4()
        mock_user = models.Usuario(
            id=user_id,
            email="usuario@example.com",
            es_superusuario=False
        )
        mock_db_session.get.return_value = mock_user
        
        # Configurar el mock para el permiso
        mock_permission = models.Permiso(
            id=uuid4(),
            nombre_recurso="documentos",
            accion="leer"
        )
        
        # Configurar el mock para la consulta de permisos del usuario
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = mock_permission
        mock_db_session.execute.return_value = mock_result
        
        # Ejecutar
        result = await permission_service.check_permission(
            user_id=user_id,
            resource="documentos",
            action="leer"
        )
        
        # Verificar que devuelve True
        assert result is True
    
    async def test_check_permission_user_without_permission(self, permission_service, mock_db_session):
        """Prueba que un usuario sin el permiso no pueda acceder."""
        # Configurar el mock para el usuario (no superusuario)
        user_id = uuid4()
        mock_user = models.Usuario(
            id=user_id,
            email="usuario@example.com",
            es_superusuario=False
        )
        mock_db_session.get.return_value = mock_user
        
        # Configurar el mock para la consulta de permisos del usuario (sin resultados)
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Ejecutar
        result = await permission_service.check_permission(
            user_id=user_id,
            resource="documentos",
            action="escribir"
        )
        
        # Verificar que devuelve False
        assert result is False
    
    async def test_get_user_permissions_superuser(self, permission_service, mock_db_session):
        """Prueba que un superusuario obtenga todos los permisos."""
        # Configurar el mock para el superusuario
        mock_user = models.Usuario(
            id=uuid4(),
            email="admin@example.com",
            es_superusuario=True
        )
        mock_db_session.get.return_value = mock_user
        
        # Configurar el mock para la consulta de todos los permisos
        mock_permissions = [
            models.Permiso(id=uuid4(), nombre_recurso="documentos", accion="leer"),
            models.Permiso(id=uuid4(), nombre_recurso="documentos", accion="escribir")
        ]
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = mock_permissions
        mock_db_session.execute.return_value = mock_result
        
        # Ejecutar
        result = await permission_service.get_user_permissions(mock_user.id)
        
        # Verificar que devuelve todos los permisos
        assert len(result) == 2
        assert all(isinstance(p, models.Permiso) for p in result)
    
    async def test_create_permission_success(self, permission_service, mock_db_session):
        """Prueba la creación exitosa de un permiso."""
        # Configurar el mock para verificar que no existe un permiso igual
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Datos para crear el permiso
        permission_data = schemas.PermissionBase(
            nombre_recurso="documentos",
            accion="leer",
            descripcion="Permiso de lectura de documentos"
        )
        
        # Configurar el mock para el commit
        mock_db_session.commit = AsyncMock()
        
        # Configurar el mock para el refresh
        new_permission = models.Permiso(
            id=uuid4(),
            **permission_data.dict()
        )
        mock_db_session.refresh = AsyncMock()
        
        # Ejecutar
        result = await permission_service.create_permission(permission_data)
        
        # Verificar que se llamó a add con un objeto Permiso
        args, _ = mock_db_session.add.call_args
        added_permission = args[0]
        assert isinstance(added_permission, models.Permiso)
        assert added_permission.nombre_recurso == "documentos"
        assert added_permission.accion == "leer"
        
        # Verificar que se hizo commit
        mock_db_session.commit.assert_awaited_once()
    
    async def test_create_permission_duplicate(self, permission_service, mock_db_session):
        """Prueba que no se pueda crear un permiso duplicado."""
        # Configurar el mock para simular que ya existe un permiso igual
        existing_permission = models.Permiso(
            id=uuid4(),
            nombre_recurso="documentos",
            accion="leer"
        )
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = existing_permission
        mock_db_session.execute.return_value = mock_result
        
        # Datos para crear el permiso (duplicado)
        permission_data = schemas.PermissionBase(
            nombre_recurso="documentos",
            accion="leer",
            descripcion="Permiso de lectura de documentos"
        )
        
        # Verificar que se lanza la excepción
        with pytest.raises(BadRequestException) as exc_info:
            await permission_service.create_permission(permission_data)
        
        assert "ya existe un permiso" in str(exc_info.value)
    
    async def test_delete_permission_success(self, permission_service, mock_db_session):
        """Prueba la eliminación exitosa de un permiso."""
        # Configurar el mock para el permiso a eliminar
        permission_id = uuid4()
        mock_permission = models.Permiso(
            id=permission_id,
            nombre_recurso="documentos",
            accion="leer"
        )
        mock_db_session.get.return_value = mock_permission
        
        # Configurar el mock para la verificación de roles con el permiso (ninguno)
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Configurar el mock para el commit
        mock_db_session.commit = AsyncMock()
        
        # Ejecutar
        result = await permission_service.delete_permission(permission_id)
        
        # Verificar que se eliminó el permiso
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_permission)
        mock_db_session.commit.assert_awaited_once()
    
    async def test_delete_permission_assigned_to_role(self, permission_service, mock_db_session):
        """Prueba que no se pueda eliminar un permiso asignado a un rol."""
        # Configurar el mock para el permiso a eliminar
        permission_id = uuid4()
        mock_permission = models.Permiso(
            id=permission_id,
            nombre_recurso="documentos",
            accion="leer"
        )
        mock_db_session.get.return_value = mock_permission
        
        # Configurar el mock para simular que el permiso está asignado a un rol
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = True  # Tiene roles asignados
        mock_db_session.execute.return_value = mock_result
        
        # Verificar que se lanza la excepción
        with pytest.raises(BadRequestException) as exc_info:
            await permission_service.delete_permission(permission_id)
        
        assert "asignado a roles" in str(exc_info.value)
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

# Se pueden agregar más pruebas para los demás servicios (AuthService, UserService, RoleService)
# siguiendo el mismo patrón que las pruebas de PermissionService.
