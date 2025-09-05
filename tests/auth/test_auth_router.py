"""
Pruebas de integración para los endpoints de autenticación.

Estas pruebas validan el flujo completo de la API, desde la autenticación
hasta las operaciones CRUD de usuarios, roles y permisos.
"""
import pytest
import pytest_asyncio
import time
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ges_neu_api.main import app
from ges_neu_api.core.config import settings
from ges_neu_api.core.database import get_session
from ges_neu_api.modules.auth import schemas, models
from tests.conftest import db_session, client

# Datos de prueba
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"
TEST_EMAIL = "test@example.com"
TEST_FULL_NAME = "Test User"

# Datos de superusuario para pruebas
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpass123"
ADMIN_EMAIL = "admin@example.com"

# Datos de rol para pruebas
TEST_ROLE_NAME = "test_role"
TEST_ROLE_DESC = "Rol de prueba"

# Fixture para crear un usuario de prueba
@pytest.fixture
def test_user() -> Dict[str, Any]:
    return {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "email": TEST_EMAIL,
        "nombre_completo": TEST_FULL_NAME,
        "activo": True
    }

# Fixture para crear un superusuario de prueba
@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    # Usar factory para crear usuario único según esquema real PostgreSQL
    import time
    from tests.auth.factories import UsuarioFactory
    
    user = await UsuarioFactory.create(
        db=db_session,
        username=f"admin_{int(time.time())}",
        email=f"admin_{int(time.time())}@example.com",
        password=ADMIN_PASSWORD,
        activo=True
    )
    return user

# Fixture para obtener token de autenticación
@pytest_asyncio.fixture
async def auth_token(admin_user, client: AsyncClient):
    # Obtener token para el usuario administrador usando username según esquema PostgreSQL
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": admin_user.username, "password": ADMIN_PASSWORD}
    )
    
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    return f"Bearer {token}"

# Fixture para cliente autenticado
@pytest_asyncio.fixture
async def auth_headers(auth_token):
    return {"Authorization": auth_token}

# Pruebas de autenticación
class TestAuth:
    @pytest.mark.asyncio
    async def test_login_success(self, admin_user, client: AsyncClient):
        """Prueba el inicio de sesión exitoso."""
        response = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": admin_user.username, "password": ADMIN_PASSWORD}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Prueba el inicio de sesión con credenciales inválidas."""
        response = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": "nonexistent", "password": "wrongpassword"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, db_session: AsyncSession, client: AsyncClient):
        """Prueba el inicio de sesión de un usuario inactivo."""
        from tests.auth.factories import UsuarioFactory
        
        # Crear usuario inactivo usando factory
        inactive_user = await UsuarioFactory.create(
            db=db_session,
            activo=False,
            username=f"inactive_user_{int(time.time())}"
        )
        
        # Intentar iniciar sesión con el usuario inactivo
        response = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": inactive_user.username, "password": "testpassword"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Inactive user" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_read_current_user(self, auth_headers, admin_user, client: AsyncClient):
        """Prueba la obtención del perfil del usuario actual."""
        response = await client.get(
            f"{settings.API_V1_STR}/auth/users/me/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == admin_user.username
        assert response.json()["email"] == admin_user.email
        assert "password_hash" not in response.json()
    
    @pytest.mark.asyncio
    async def test_read_current_user_unauthorized(self, client: AsyncClient):
        """Prueba el acceso no autorizado al perfil de usuario."""
        response = await client.get(
            f"{settings.API_V1_STR}/auth/users/me/"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]

# Pruebas de gestión de usuarios
class TestUserManagement:
    """Pruebas para la gestión de usuarios."""
    
    @pytest.mark.asyncio
    async def test_create_user(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Prueba la creación de un nuevo usuario."""
        # Arrange - Datos alineados con esquema PostgreSQL
        timestamp = int(time.time())
        user_data = {
            "username": f"newuser_{timestamp}",
            "email": f"newuser_{timestamp}@example.com",
            "password": "NewUserPass123!",
            "nombre_completo": "New User",
            "activo": True
        }
        
        # Act
        response = await client.post(
            f"{settings.API_V1_STR}/auth/users/",
            json=user_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        created_user = response.json()
        assert created_user["username"] == user_data["username"]
        assert created_user["email"] == user_data["email"]
        assert created_user["nombre_completo"] == user_data["nombre_completo"]
        assert "password" not in created_user
        
        # Verificar que el usuario se creó en la base de datos
        from sqlalchemy import select
        from ges_neu_api.modules.auth.models import Usuario
        user = await db_session.execute(
            select(Usuario).where(Usuario.username == user_data["username"])
        )
        user = user.scalar_one_or_none()
        assert user is not None
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        admin_user: models.Usuario
    ):
        """Prueba la creación de un usuario con un nombre de usuario duplicado."""
        # Arrange
        user_data = {
            "username": admin_user.username,  # Usuario ya existente
            "email": "different@example.com",
            "password": "TestPass123!",
            "nombre_completo": "Duplicate User",
            "activo": True,
            "rol": "user"
        }
        
        # Act
        response = await client.post(
            f"{settings.API_V1_STR}/auth/users/",
            json=user_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_list_users(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        admin_user: models.Usuario
    ):
        """Prueba la obtención de la lista de usuarios."""
        # Act
        response = await client.get(
            f"{settings.API_V1_STR}/auth/users/",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert isinstance(users, list)
        assert any(user["username"] == admin_user.username for user in users)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        admin_user: models.Usuario
    ):
        """Prueba la obtención de un usuario por su ID."""
        # Act
        response = await client.get(
            f"{settings.API_V1_STR}/auth/users/{admin_user.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["id"] == str(admin_user.id)
        assert user_data["username"] == admin_user.username
        assert "password" not in user_data
    
    @pytest.mark.asyncio
    async def test_update_user(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        admin_user: models.Usuario
    ):
        """Prueba la actualización de un usuario existente."""
        # Arrange
        update_data = {
            "email": "updated@example.com",
            "nombre_completo": "Updated Name",
            "activo": False
        }
        
        # Act
        response = await client.patch(
            f"{settings.API_V1_STR}/auth/users/{admin_user.id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        updated_user = response.json()
        assert updated_user["email"] == update_data["email"]
        assert updated_user["nombre_completo"] == update_data["nombre_completo"]
        assert updated_user["activo"] == update_data["activo"]
    
    @pytest.mark.asyncio
    async def test_change_password(
        self,
        client: AsyncClient,
        auth_headers: dict,
        admin_user: models.Usuario,
        db_session: AsyncSession
    ):
        """Prueba el cambio de contraseña de un usuario."""
        # Arrange
        password_data = {
            "current_password": ADMIN_PASSWORD,
            "new_password": "NewAdminPass123!"
        }
        
        # Act
        response = await client.post(
            f"{settings.API_V1_STR}/auth/users/{admin_user.id}/change-password",
            json=password_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que la contraseña se actualizó en la base de datos
        await db_session.refresh(admin_user)
        assert admin_user.verify_password(password_data["new_password"])
        
        # Restaurar la contraseña original para otras pruebas
        from ges_neu_api.modules.auth.utils import get_password_hash
        admin_user.password_hash = get_password_hash(ADMIN_PASSWORD)
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Prueba la eliminación lógica de un usuario."""
        # Crear un usuario para eliminar usando factory
        from tests.auth.factories import UsuarioFactory
        
        user = await UsuarioFactory.create(
            db=db_session,
            username=f"tobedeleted_{int(time.time())}",
            email=f"delete_{int(time.time())}@example.com",
            activo=True
        )
        
        # Act
        response = await client.delete(
            f"{settings.API_V1_STR}/auth/users/{user.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que el usuario se marcó como inactivo
        await db_session.refresh(user)
        assert user.activo is False

# Pruebas de gestión de roles
class TestRoles:
    """Pruebas para la gestión de roles."""
    
    @pytest.mark.asyncio
    async def test_create_role(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la creación de un nuevo rol."""
        role_data = {
            "nombre": "test_role",
            "descripcion": "Rol de prueba",
            "es_rol_sistema": False
        }
        
        response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == role_data["nombre"]
        assert data["descripcion"] == role_data["descripcion"]
        assert data["es_rol_sistema"] == role_data["es_rol_sistema"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_duplicate_role(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la creación de un rol con un nombre duplicado."""
        role_data = {
            "nombre": "duplicate_role",
            "descripcion": "Rol duplicado",
            "es_rol_sistema": False
        }
        
        # Crear el rol por primera vez
        response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Intentar crear el mismo rol de nuevo
        response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Ya existe un rol con este nombre" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_roles(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la obtención de la lista de roles."""
        response = await client.get(
            f"{settings.API_V1_STR}/auth/roles/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_role_by_id(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la obtención de un rol por su ID."""
        # Primero creamos un rol
        role_data = {
            "nombre": "test_get_role",
            "descripcion": "Rol para prueba de obtención",
            "es_rol_sistema": False
        }
        
        create_response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        role_id = create_response.json()["id"]
        
        # Ahora lo obtenemos
        response = await client.get(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == role_id
        assert data["nombre"] == role_data["nombre"]
    
    @pytest.mark.asyncio
    async def test_update_role(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la actualización de un rol existente."""
        # Crear un rol para actualizar
        role_data = {
            "nombre": "test_update_role",
            "descripcion": "Rol para prueba de actualización",
            "es_rol_sistema": False
        }
        
        create_response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        role_id = create_response.json()["id"]
        
        # Actualizar el rol
        update_data = {
            "nombre": "test_updated_role",
            "descripcion": "Descripción actualizada"
        }
        
        response = await client.put(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == update_data["nombre"]
        assert data["descripcion"] == update_data["descripcion"]
    
    @pytest.mark.asyncio
    async def test_delete_role(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la eliminación de un rol."""
        # Crear un rol para eliminar
        role_data = {
            "nombre": "test_delete_role",
            "descripcion": "Rol para prueba de eliminación",
            "es_rol_sistema": False
        }
        
        create_response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        role_id = create_response.json()["id"]
        
        # Eliminar el rol
        response = await client.delete(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que el rol ya no existe
        get_response = await client.get(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_assign_role_to_user(self, client: AsyncClient, auth_headers, admin_user, db_session: AsyncSession):
        """Prueba la asignación de un rol a un usuario."""
        # Crear un rol
        role_data = {
            "nombre": "test_assign_role",
            "descripcion": "Rol para prueba de asignación",
            "es_rol_sistema": False
        }
        
        role_response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        role_id = role_response.json()["id"]
        
        # Crear un usuario
        user_data = {
            "username": "testuser_role_assign",
            "password": "testpass123",
            "email": "test_role_assign@example.com",
            "nombre_completo": "Test User Role Assign"
        }
        
        user_response = await client.post(
            f"{settings.API_V1_STR}/auth/users/",
            json=user_data,
            headers=auth_headers
        )
        user_id = user_response.json()["id"]
        
        # Asignar el rol al usuario
        response = await client.post(
            f"{settings.API_V1_STR}/auth/users/{user_id}/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert any(role["id"] == role_id for role in response.json()["roles"])
    
    @pytest.mark.asyncio
    async def test_revoke_role_from_user(self, client: AsyncClient, auth_headers, admin_user, db_session: AsyncSession):
        """Prueba la revocación de un rol a un usuario."""
        # Crear un rol
        role_data = {
            "nombre": "test_revoke_role",
            "descripcion": "Rol para prueba de revocación",
            "es_rol_sistema": False
        }
        
        role_response = await client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        role_id = role_response.json()["id"]
        
        # Crear un usuario
        user_data = {
            "username": "testuser_role_revoke",
            "password": "testpass123",
            "email": "test_role_revoke@example.com",
            "nombre_completo": "Test User Role Revoke"
        }
        
        user_response = await client.post(
            f"{settings.API_V1_STR}/auth/users/",
            json=user_data,
            headers=auth_headers
        )
        user_id = user_response.json()["id"]
        
        # Asignar el rol al usuario primero
        assign_response = await client.post(
            f"{settings.API_V1_STR}/auth/users/{user_id}/roles/{role_id}",
            headers=auth_headers
        )
        assert assign_response.status_code == status.HTTP_200_OK
        
        # Revocar el rol
        response = await client.delete(
            f"{settings.API_V1_STR}/auth/users/{user_id}/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert not any(role["id"] == role_id for role in response.json()["roles"])

# Pruebas de permisos
class TestPermissions:
    @pytest.mark.asyncio
    async def test_check_permission(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la verificación de un permiso."""
        response = await client.get(
            f"{settings.API_V1_STR}/auth/permissions/check?resource=users&action=read",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "has_permission" in response.json()
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(self, client: AsyncClient, auth_headers, admin_user):
        """Prueba la obtención de permisos de un usuario."""
        response = await client.get(
            f"{settings.API_V1_STR}/auth/users/{admin_user.id}/permissions",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
