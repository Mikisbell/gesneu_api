"""
Pruebas para los servicios de autenticación y usuarios.

Este módulo contiene pruebas unitarias para los servicios de autenticación
y gestión de usuarios.
"""
import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4, UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.modules.auth.service import AuthService, UserService, RoleService, PermissionService
from ges_neu_api.modules.auth import models, schemas
from core.config import settings
from core.security import get_password_hash, verify_password
from core.exceptions import UnauthorizedException, BadRequestException

# Datos de prueba
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"
TEST_EMAIL = "test@example.com"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"
TEST_USER_ID = uuid4()

# Fixture para el mock de la sesión de base de datos
@pytest.fixture
def mock_db_session():
    """Crea una sesión de base de datos simulada para pruebas."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock(side_effect=lambda x: x)
    
    # Configurar los mocks anidados
    execute_result = AsyncMock()
    scalars_result = MagicMock()
    scalars_result.first.return_value = None
    execute_result.scalars.return_value = scalars_result
    session.execute.return_value = execute_result
    
    return session

# Fixture para un usuario de prueba
@pytest.fixture
def test_user():
    """Crea un usuario de prueba."""
    return models.Usuario(
        id=TEST_USER_ID,
        username=TEST_USERNAME,
        password_hash=get_password_hash(TEST_PASSWORD),
        email=TEST_EMAIL,
        nombre_completo=f"{TEST_FIRST_NAME} {TEST_LAST_NAME}",
        activo=True,
        creado_en=datetime.utcnow(),
        actualizado_en=datetime.utcnow(),
    )

# Fixture para datos de creación de usuario
@pytest.fixture
def test_user_create():
    """Crea datos de prueba para crear un usuario."""
    return schemas.UsuarioCreate(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        nombre_completo=f"{TEST_FIRST_NAME} {TEST_LAST_NAME}",
        password=TEST_PASSWORD,
        creado_por=TEST_USER_ID
    )

# Fixture para datos de actualización de usuario
@pytest.fixture
def test_user_update():
    """Crea datos de prueba para actualizar un usuario."""
    return schemas.UsuarioUpdate(
        email="updated@example.com",
        nombre_completo="Updated User",
        activo=False
    )

# Fixture para un rol de prueba
@pytest.fixture
def test_role():
    """Crea un rol de prueba."""
    return models.Rol(
        id=uuid4(),
        nombre="test_role",
        descripcion="Rol de prueba",
        es_rol_sistema=False,
        creado_en=datetime.utcnow()
    )

# Fixture para una relación usuario-rol de prueba
@pytest.fixture
def test_user_role(test_user, test_role):
    """Crea una relación usuario-rol de prueba."""
    return models.UsuariosRoles(
        usuario_id=test_user.id,
        rol_id=test_role.id,
        asignado_en=datetime.utcnow(),
        asignado_por=test_user.id
    )

# Fixture para un permiso de prueba
@pytest.fixture
def test_permission():
    """Crea un permiso de prueba."""
    return models.Permiso(
        id=uuid4(),
        nombre_recurso="test_resource",
        accion="read",
        descripcion="Permiso de prueba para leer recursos",
        creado_en=datetime.utcnow()
    )

# Fixture para una relación rol-permiso de prueba
@pytest.fixture
def test_role_permission(test_role, test_permission):
    """Crea una relación rol-permiso de prueba."""
    return models.RolesPermisos(
        rol_id=test_role.id,
        permiso_id=test_permission.id,
        asignado_en=datetime.utcnow(),
        asignado_por=TEST_USER_ID
    )

# Pruebas para UserService
class TestUserService:
    """Pruebas para el servicio de gestión de usuarios."""
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, mock_db_session, test_user):
        """Prueba obtener un usuario por ID cuando existe."""
        # Configurar el mock para devolver el usuario de prueba
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_user
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.get_user_by_id(TEST_USER_ID)
        
        # Verificar resultados
        assert result is not None
        assert result.id == TEST_USER_ID
        assert result.username == TEST_USERNAME
        
        # Verificar que se llamó a execute con la consulta correcta
        mock_db_session.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db_session):
        """Prueba obtener un usuario por ID cuando no existe."""
        # Configurar el mock para devolver None (usuario no encontrado)
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.get_user_by_id(TEST_USER_ID)
        
        # Verificar que el resultado es None
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_found(self, mock_db_session, test_user):
        """Prueba obtener un usuario por nombre de usuario cuando existe."""
        # Configurar el mock para devolver el usuario de prueba
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_user
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.get_user_by_username(TEST_USERNAME)
        
        # Verificar resultados
        assert result is not None
        assert result.username == TEST_USERNAME
        
        # Verificar que se llamó a execute con la consulta correcta
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db_session, test_user_create):
        """Prueba la creación exitosa de un usuario."""
        # Configurar el mock para simular que no existe un usuario con el mismo nombre
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.create_user(test_user_create)
        
        # Verificar resultados
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.email == TEST_EMAIL
        assert result.nombre_completo == f"{TEST_FIRST_NAME} {TEST_LAST_NAME}"
        
        # Verificar que se llamó a add, commit y refresh
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, mock_db_session, test_user, test_user_create):
        """Prueba la creación de un usuario con un nombre de usuario que ya existe."""
        # Configurar el mock para simular que ya existe un usuario con el mismo nombre
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_user
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Verificar que se lanza la excepción correcta
        with pytest.raises(BadRequestException) as exc_info:
            await user_service.create_user(test_user_create)
        
        # Verificar el mensaje de error
        assert "ya existe" in str(exc_info.value.message).lower()
        assert exc_info.value.code == "user_already_exists"
        
        # Verificar que no se llamó a commit ni a refresh
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_db_session, test_user, test_user_update):
        """Prueba la actualización exitosa de un usuario."""
        # Configurar el mock para devolver el usuario de prueba
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_user
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.update_user(TEST_USER_ID, test_user_update)
        
        # Verificar resultados
        assert result is not None
        assert result.email == test_user_update.email
        assert result.nombre_completo == test_user_update.nombre_completo
        assert result.activo == test_user_update.activo
        
        # Verificar que se actualizó la fecha de actualización
        assert test_user.actualizado_en is not None
        
        # Verificar que se llamó a commit y refresh
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_db_session, test_user_update):
        """Prueba la actualización de un usuario que no existe."""
        # Configurar el mock para devolver None (usuario no encontrado)
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.update_user(TEST_USER_ID, test_user_update)
        
        # Verificar que el resultado es None
        assert result is None
        
        # Verificar que no se llamó a commit ni a refresh
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_user_password(self, mock_db_session, test_user):
        """Prueba la actualización de la contraseña de un usuario."""
        # Configurar el mock para devolver el usuario de prueba
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_user
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Nuevo password para la prueba
        new_password = "nuevacontraseña123"
        update_data = schemas.UsuarioUpdate(password=new_password)
        
        # Llamar al método bajo prueba
        result = await user_service.update_user(TEST_USER_ID, update_data)
        
        # Verificar resultados
        assert result is not None
        
        # Verificar que la contraseña se ha actualizado correctamente
        assert test_user.password_hash != get_password_hash(TEST_PASSWORD)
        assert verify_password(new_password, test_user.password_hash)
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, mock_db_session, test_user):
        """Prueba la eliminación exitosa de un usuario."""
        # Configurar el mock para devolver el usuario de prueba
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_user
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.delete_user(TEST_USER_ID)
        
        # Verificar resultados
        assert result is True
        
        # Verificar que se llamó a delete, commit y refresh
        mock_db_session.delete.assert_called_once_with(test_user)
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_db_session):
        """Prueba la eliminación de un usuario que no existe."""
        # Configurar el mock para devolver None (usuario no encontrado)
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await user_service.delete_user(TEST_USER_ID)
        
        # Verificar que el resultado es False
        assert result is False
        
        # Verificar que no se llamó a delete ni a commit
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

# Pruebas para RoleService
class TestRoleService:
    """Pruebas para el servicio de gestión de roles."""
    
    @pytest.mark.asyncio
    async def test_assign_role_to_user_success(self, mock_db_session, test_user, test_role):
        """Prueba la asignación exitosa de un rol a un usuario."""
        # Configurar los mocks para simular que el usuario y el rol existen
        mock_db_session.execute.side_effect = [
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=test_user)))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=test_role)))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        ]
        
        # Crear instancia del servicio
        role_service = RoleService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await role_service.assign_role_to_user(
            user_id=test_user.id,
            role_id=test_role.id
        )
        
        # Verificar resultados
        assert result is True
        
        # Verificar que se llamó a add, commit y refresh
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_assign_role_to_user_already_assigned(self, mock_db_session, test_user, test_role, test_user_role):
        """Prueba la asignación de un rol que ya estaba asignado."""
        # Configurar los mocks para simular que el usuario y el rol existen
        # y que ya existe la asignación
        mock_db_session.execute.side_effect = [
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=test_user)))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=test_role)))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=test_user_role)))),
        ]
        
        # Crear instancia del servicio
        role_service = RoleService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await role_service.assign_role_to_user(
            user_id=test_user.id,
            role_id=test_role.id
        )
        
        # Verificar que devuelve True (la asignación ya existía)
        assert result is True
        
        # Verificar que no se intentó crear una nueva asignación
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_assign_role_to_nonexistent_user(self, mock_db_session, test_role):
        """Prueba la asignación de un rol a un usuario que no existe."""
        # Configurar el mock para simular que el usuario no existe
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
        
        # Crear instancia del servicio
        role_service = RoleService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await role_service.assign_role_to_user(
            user_id=uuid4(),
            role_id=test_role.id
        )
        
        # Verificar que devuelve False
        assert result is False
        
        # Verificar que no se intentó crear ninguna asignación
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_assign_nonexistent_role_to_user(self, mock_db_session, test_user):
        """Prueba la asignación de un rol que no existe a un usuario."""
        # Configurar los mocks para simular que el usuario existe pero el rol no
        mock_db_session.execute.side_effect = [
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=test_user)))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        ]
        
        # Crear instancia del servicio
        role_service = RoleService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await role_service.assign_role_to_user(
            user_id=test_user.id,
            role_id=uuid4()
        )
        
        # Verificar que devuelve False
        assert result is False
        
        # Verificar que no se intentó crear ninguna asignación
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_revoke_role_from_user_success(self, mock_db_session, test_user, test_role, test_user_role):
        """Prueba la revocación exitosa de un rol a un usuario."""
        # Configurar el mock para simular que existe la asignación
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_user_role
        
        # Crear instancia del servicio
        role_service = RoleService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await role_service.revoke_role_from_user(
            user_id=test_user.id,
            role_id=test_role.id
        )
        
        # Verificar resultados
        assert result is True
        
        # Verificar que se llamó a delete y commit
        mock_db_session.delete.assert_called_once_with(test_user_role)
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_revoke_nonexistent_assignment(self, mock_db_session, test_user, test_role):
        """Prueba la revocación de una asignación que no existe."""
        # Configurar el mock para simular que no existe la asignación
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
        
        # Crear instancia del servicio
        role_service = RoleService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await role_service.revoke_role_from_user(
            user_id=test_user.id,
            role_id=test_role.id
        )
        
        # Verificar que devuelve False
        assert result is False
        
        # Verificar que no se intentó eliminar nada
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

# Pruebas para PermissionService
class TestPermissionService:
    """Pruebas para el servicio de gestión de permisos."""
    
    @pytest.mark.asyncio
    async def test_check_permission_success(self, mock_db_session, test_user, test_role, test_permission, test_user_role, test_role_permission):
        """Prueba la verificación exitosa de un permiso."""
        # Configurar los mocks para simular que el usuario tiene el permiso
        mock_db_session.execute.side_effect = [
            # Para check_permission -> get_user_permissions
            MagicMock(fetchall=MagicMock(return_value=[
                (test_permission.nombre_recurso, test_permission.accion)
            ])),
        ]
        
        # Crear instancia del servicio
        permission_service = PermissionService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await permission_service.check_permission(
            user_id=test_user.id,
            resource=test_permission.nombre_recurso,
            action=test_permission.accion
        )
        
        # Verificar resultados
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_permission_denied(self, mock_db_session, test_user):
        """Prueba la verificación de un permiso que el usuario no tiene."""
        # Configurar el mock para simular que el usuario no tiene permisos
        mock_db_session.execute.return_value.fetchall.return_value = []
        
        # Crear instancia del servicio
        permission_service = PermissionService(mock_db_session)
        
        # Llamar al método bajo prueba
        result = await permission_service.check_permission(
            user_id=test_user.id,
            resource="nonexistent_resource",
            action="write"
        )
        
        # Verificar que el permiso fue denegado
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(self, mock_db_session, test_user, test_permission):
        """Prueba la obtención de permisos de un usuario."""
        # Configurar el mock para devolver los permisos del usuario
        mock_db_session.execute.return_value.fetchall.return_value = [
            (test_permission.nombre_recurso, test_permission.accion)
        ]
        
        # Crear instancia del servicio
        permission_service = PermissionService(mock_db_session)
        
        # Llamar al método bajo prueba
        permissions = await permission_service.get_user_permissions(
            user_id=test_user.id
        )
        
        # Verificar resultados
        assert len(permissions) == 1
        assert permissions[0]["nombre_recurso"] == test_permission.nombre_recurso
        assert permissions[0]["accion"] == test_permission.accion
        
        # Verificar que se ejecutó la consulta SQL correcta
        mock_db_session.execute.assert_called_once()
        
        # Verificar que los parámetros de la consulta son correctos
        called_args = mock_db_session.execute.call_args[1]
        assert called_args["user_id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_user_permissions_empty(self, mock_db_session, test_user):
        """Prueba la obtención de permisos cuando el usuario no tiene ninguno."""
        # Configurar el mock para devolver una lista vacía de permisos
        mock_db_session.execute.return_value.fetchall.return_value = []
        
        # Crear instancia del servicio
        permission_service = PermissionService(mock_db_session)
        
        # Llamar al método bajo prueba
        permissions = await permission_service.get_user_permissions(
            user_id=test_user.id
        )
        
        # Verificar que no se devolvieron permisos
        assert len(permissions) == 0