"""
Pruebas de integración para los endpoints de autenticación.

Estas pruebas validan el flujo completo de la API, desde la autenticación
hasta las operaciones CRUD de usuarios, roles y permisos.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.main import app
from core.config import settings
from core.database import Base, get_session, engine
from modules.auth import schemas, models
from tests.conftest import async_test_db, override_get_db

# Configurar el cliente de prueba
client = TestClient(app)

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
        "full_name": TEST_FULL_NAME,
        "is_active": True,
        "is_superuser": False
    }

# Fixture para crear un superusuario de prueba
@pytest.fixture
async def admin_user(db: AsyncSession):
    # Crear un usuario administrador
    admin_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "email": ADMIN_EMAIL,
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True
    }
    
    user = models.Usuario(**admin_data)
    user.set_password(ADMIN_PASSWORD)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Fixture para obtener token de autenticación
@pytest.fixture
async def auth_token(admin_user):
    # Obtener token para el usuario administrador
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": login_data["username"], "password": login_data["password"]}
    )
    
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    return f"Bearer {token}"

# Fixture para cliente autenticado
@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": auth_token}

# Pruebas de autenticación
class TestAuth:
    def test_login_success(self, admin_user):
        """Prueba el inicio de sesión exitoso."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/token",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Prueba el inicio de sesión con credenciales inválidas."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/token",
            data={"username": "nonexistent", "password": "wrongpassword"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, admin_user):
        """Prueba el inicio de sesión de un usuario inactivo."""
        # Crear un usuario inactivo
        inactive_user = models.Usuario(
            username="inactive_user",
            email="inactive@example.com",
            password="TestPass123!",
            is_active=False,
            is_superuser=False
        )
        inactive_user.set_password("TestPass123!")
        db = get_session()
        db.add(inactive_user)
        db.commit()
        db.refresh(inactive_user)
        
        # Intentar iniciar sesión con el usuario inactivo
        response = client.post(
            f"{settings.API_V1_STR}/auth/token",
            data={"username": "inactive_user", "password": "TestPass123!"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in response.json()["detail"]
    
    def test_read_current_user(self, auth_headers):
        """Prueba la obtención del perfil del usuario actual."""
        response = client.get(
            f"{settings.API_V1_STR}/auth/users/me/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == ADMIN_USERNAME
        assert response.json()["email"] == ADMIN_EMAIL
        assert "hashed_password" not in response.json()
    
    def test_read_current_user_unauthorized(self):
        """Prueba el acceso no autorizado al perfil de usuario."""
        response = client.get(
            f"{settings.API_V1_STR}/auth/users/me/"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]

# Pruebas de gestión de usuarios
class TestUserManagement:
    """Pruebas para la gestión de usuarios."""
    
    async def test_create_user(
        self, 
        client: TestClient, 
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Prueba la creación de un nuevo usuario."""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewUserPass123!",
            "nombre_completo": "New User",
            "activo": True,
            "rol": "user"
        }
        
        # Act
        response = client.post(
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
        user = await db_session.execute(
            select(Usuario).where(Usuario.username == user_data["username"])
        )
        user = user.scalar_one_or_none()
        assert user is not None
    
    async def test_create_user_duplicate_username(
        self, 
        client: TestClient, 
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
        response = client.post(
            f"{settings.API_V1_STR}/auth/users/",
            json=user_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    async def test_list_users(
        self, 
        client: TestClient, 
        auth_headers: dict,
        admin_user: models.Usuario
    ):
        """Prueba la obtención de la lista de usuarios."""
        # Act
        response = client.get(
            f"{settings.API_V1_STR}/auth/users/",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert isinstance(users, list)
        assert any(user["username"] == admin_user.username for user in users)
    
    async def test_get_user_by_id(
        self, 
        client: TestClient, 
        auth_headers: dict,
        admin_user: models.Usuario
    ):
        """Prueba la obtención de un usuario por su ID."""
        # Act
        response = client.get(
            f"{settings.API_V1_STR}/auth/users/{admin_user.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["id"] == str(admin_user.id)
        assert user_data["username"] == admin_user.username
        assert "password" not in user_data
    
    async def test_update_user(
        self, 
        client: TestClient, 
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
        response = client.patch(
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
    
    async def test_change_password(
        self,
        client: TestClient,
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
        response = client.post(
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
        admin_user.password_hash = get_password_hash(ADMIN_PASSWORD)
        await db_session.commit()
    
    async def test_delete_user(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Prueba la eliminación lógica de un usuario."""
        # Crear un usuario para eliminar
        user = models.Usuario(
            username="tobedeleted",
            email="delete@example.com",
            password_hash=get_password_hash("TestPass123!"),
            activo=True,
            rol="user"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Act
        response = client.delete(
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
    
    def test_create_role(self, auth_headers, admin_user):
        """Prueba la creación de un nuevo rol."""
        role_data = {
            "nombre": "test_role",
            "descripcion": "Rol de prueba",
            "es_rol_sistema": False
        }
        
        response = client.post(
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
    
    def test_create_duplicate_role(self, auth_headers, admin_user):
        """Prueba la creación de un rol con un nombre duplicado."""
        role_data = {
            "nombre": "duplicate_role",
            "descripcion": "Rol duplicado",
            "es_rol_sistema": False
        }
        
        # Crear el rol por primera vez
        response = client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Intentar crear el mismo rol de nuevo
        response = client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Ya existe un rol con este nombre" in response.json()["detail"]
    
    def test_get_roles(self, auth_headers, admin_user):
        """Prueba la obtención de la lista de roles."""
        response = client.get(
            f"{settings.API_V1_STR}/auth/roles/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_get_role_by_id(self, auth_headers, admin_user):
        """Prueba la obtención de un rol por su ID."""
        # Primero creamos un rol
        role_data = {
            "nombre": "test_get_role",
            "descripcion": "Rol para prueba de obtención",
            "es_rol_sistema": False
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        role_id = create_response.json()["id"]
        
        # Ahora lo obtenemos
        response = client.get(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == role_id
        assert data["nombre"] == role_data["nombre"]
    
    def test_update_role(self, auth_headers, admin_user):
        """Prueba la actualización de un rol existente."""
        # Crear un rol para actualizar
        role_data = {
            "nombre": "test_update_role",
            "descripcion": "Rol para prueba de actualización",
            "es_rol_sistema": False
        }
        
        create_response = client.post(
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
        
        response = client.put(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == update_data["nombre"]
        assert data["descripcion"] == update_data["descripcion"]
    
    def test_delete_role(self, auth_headers, admin_user):
        """Prueba la eliminación de un rol."""
        # Crear un rol para eliminar
        role_data = {
            "nombre": "test_delete_role",
            "descripcion": "Rol para prueba de eliminación",
            "es_rol_sistema": False
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/auth/roles/",
            json=role_data,
            headers=auth_headers
        )
        role_id = create_response.json()["id"]
        
        # Eliminar el rol
        response = client.delete(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que el rol ya no existe
        get_response = client.get(
            f"{settings.API_V1_STR}/auth/roles/{role_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_assign_role_to_user(self, auth_headers, admin_user, db: AsyncSession):
        """Prueba la asignación de un rol a un usuario."""
        # Crear un rol
        role_data = {
            "nombre": "test_assign_role",
            "descripcion": "Rol para prueba de asignación",
            "es_rol_sistema": False
        }
        
        role_response = client.post(
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
            "full_name": "Test User Role Assign"
        }
        
        user_response = client.post(
            f"{settings.API_V1_STR}/auth/users/",
            json=user_data,
            headers=auth_headers
        )
        user_id = user_response.json()["id"]
        
        # Asignar el rol al usuario
        response = client.post(
            f"{settings.API_V1_STR}/auth/users/{user_id}/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert any(role["id"] == role_id for role in response.json()["roles"])
    
    def test_revoke_role_from_user(self, auth_headers, admin_user, db: AsyncSession):
        """Prueba la revocación de un rol a un usuario."""
        # Crear un rol
        role_data = {
            "nombre": "test_revoke_role",
            "descripcion": "Rol para prueba de revocación",
            "es_rol_sistema": False
        }
        
        role_response = client.post(
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
            "full_name": "Test User Role Revoke"
        }
        
        user_response = client.post(
            f"{settings.API_V1_STR}/auth/users/",
            json=user_data,
            headers=auth_headers
        )
        user_id = user_response.json()["id"]
        
        # Asignar el rol al usuario primero
        assign_response = client.post(
            f"{settings.API_V1_STR}/auth/users/{user_id}/roles/{role_id}",
            headers=auth_headers
        )
        assert assign_response.status_code == status.HTTP_200_OK
        
        # Revocar el rol
        response = client.delete(
            f"{settings.API_V1_STR}/auth/users/{user_id}/roles/{role_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert not any(role["id"] == role_id for role in response.json()["roles"])

# Pruebas de permisos
class TestPermissions:
    def test_check_permission(self, auth_headers, admin_user):
        """Prueba la verificación de un permiso."""
        response = client.get(
            f"{settings.API_V1_STR}/auth/permissions/check?resource=users&action=read",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "has_permission" in response.json()
    
    def test_get_user_permissions(self, auth_headers, admin_user):
        """Prueba la obtención de permisos de un usuario."""
        response = client.get(
            f"{settings.API_V1_STR}/auth/users/{admin_user.id}/permissions",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
