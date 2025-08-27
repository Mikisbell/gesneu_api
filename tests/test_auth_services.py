"""
Pruebas para los servicios de autenticación y usuarios.

Este módulo contiene pruebas unitarias para los servicios de autenticación
y gestión de usuarios.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.auth.service import AuthService, UserService
from ges_neu_api.auth.models.usuario import Usuario
from ges_neu_api.core.security import get_password_hash, verify_password

# Datos de prueba
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"
TEST_EMAIL = "test@example.com"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"

# Fixture para el mock de la sesión de base de datos
@pytest.fixture
def mock_db_session():
    """Crea una sesión de base de datos simulada para pruebas."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=lambda x: x)
    return session

# Fixture para un usuario de prueba
@pytest.fixture
def test_user():
    """Crea un usuario de prueba."""
    return Usuario(
        id=1,
        username=TEST_USERNAME,
        password_hash=get_password_hash(TEST_PASSWORD),
        email=TEST_EMAIL,
        nombre=TEST_FIRST_NAME,
        apellido=TEST_LAST_NAME,
        activo=True,
        creado_en=datetime.utcnow(),
        actualizado_en=datetime.utcnow(),
    )

# Pruebas para AuthService
class TestAuthService:
    """Pruebas para el servicio de autenticación."""
    
    async def test_authenticate_user_success(self, mock_db_session, test_user):
        """Prueba la autenticación exitosa de un usuario."""
        # Configurar el mock para devolver el usuario de prueba
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        # Crear instancia del servicio
        auth_service = AuthService(mock_db_session)
        
        # Ejecutar la autenticación
        user = await auth_service.authenticate_user(TEST_USERNAME, TEST_PASSWORD)
        
        # Verificar resultados
        assert user is not None
        assert user.username == TEST_USERNAME
        assert user.email == TEST_EMAIL
        mock_db_session.commit.assert_called_once()
    
    async def test_authenticate_user_wrong_password(self, mock_db_session, test_user):
        """Prueba la autenticación con contraseña incorrecta."""
        # Configurar el mock para devolver el usuario de prueba
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        # Crear instancia del servicio
        auth_service = AuthService(mock_db_session)
        
        # Ejecutar la autenticación con contraseña incorrecta
        user = await auth_service.authenticate_user(TEST_USERNAME, "wrongpassword")
        
        # Verificar que no se autenticó
        assert user is None
    
    async def test_create_access_token(self):
        """Prueba la creación de un token de acceso."""
        # Crear instancia del servicio con una sesión nula (no se usa en este método)
        auth_service = AuthService(None)
        
        # Crear token
        token_data = {"sub": TEST_USERNAME}
        token = auth_service.create_access_token(token_data)
        
        # Verificar que se creó el token
        assert isinstance(token, str)
        assert len(token) > 0

# Pruebas para UserService
class TestUserService:
    """Pruebas para el servicio de usuarios."""
    
    async def test_create_user_success(self, mock_db_session):
        """Prueba la creación exitosa de un usuario."""
        # Configurar el mock para simular que no existe un usuario con el mismo nombre
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Datos del nuevo usuario
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "nombre": "New",
            "apellido": "User"
        }
        
        # Crear usuario
        user = await user_service.create_user(user_data)
        
        # Verificar resultados
        assert user is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.nombre == user_data["nombre"]
        assert user.apellido == user_data["apellido"]
        assert verify_password(user_data["password"], user.password_hash)
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    async def test_get_user_by_id(self, mock_db_session, test_user):
        """Prueba la obtención de un usuario por ID."""
        # Configurar el mock para devolver el usuario de prueba
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Obtener usuario
        user = await user_service.get_user_by_id(test_user.id)
        
        # Verificar resultados
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
    
    async def test_update_user(self, mock_db_session, test_user):
        """Prueba la actualización de un usuario existente."""
        # Configurar el mock para devolver el usuario de prueba
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Datos de actualización
        update_data = {
            "nombre": "Updated",
            "apellido": "Name",
            "email": "updated@example.com"
        }
        
        # Actualizar usuario
        updated_user = await user_service.update_user(test_user.id, update_data)
        
        # Verificar resultados
        assert updated_user is not None
        assert updated_user.nombre == update_data["nombre"]
        assert updated_user.apellido == update_data["apellido"]
        assert updated_user.email == update_data["email"]
        mock_db_session.commit.assert_called_once()
    
    async def test_delete_user(self, mock_db_session, test_user):
        """Prueba la eliminación lógica de un usuario."""
        # Configurar el mock para devolver el usuario de prueba
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        # Crear instancia del servicio
        user_service = UserService(mock_db_session)
        
        # Eliminar usuario
        result = await user_service.delete_user(test_user.id)
        
        # Verificar resultados
        assert result is True
        assert not test_user.activo
        mock_db_session.commit.assert_called_once()

# Pruebas de integración entre AuthService y UserService
class TestAuthIntegration:
    """Pruebas de integración entre los servicios de autenticación y usuarios."""
    
    async def test_register_and_authenticate_user(self, mock_db_session):
        """Prueba el flujo completo de registro y autenticación de un usuario."""
        # Configurar el mock para simular que no existe un usuario con el mismo nombre
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Crear instancias de los servicios
        user_service = UserService(mock_db_session)
        auth_service = AuthService(mock_db_session)
        
        # 1. Registrar un nuevo usuario
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "nombre": "New",
            "apellido": "User"
        }
        
        user = await user_service.create_user(user_data)
        assert user is not None
        
        # 2. Configurar el mock para devolver el usuario recién creado
        mock_result.scalars.return_value.first.return_value = user
        
        # 3. Autenticar al usuario
        authenticated_user = await auth_service.authenticate_user(
            user_data["username"], 
            user_data["password"]
        )
        
        # Verificar que la autenticación fue exitosa
        assert authenticated_user is not None
        assert authenticated_user.username == user_data["username"]
        
        # 4. Generar token de acceso
        token = auth_service.create_access_token({"sub": authenticated_user.username})
        assert token is not None
        
        # 5. Verificar el token
        current_user = await auth_service.get_current_user(token)
        assert current_user is not None
        assert current_user.username == user_data["username"]
