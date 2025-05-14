# tests/test_usuarios.py (Versión Completa y Corregida con Prefijo API)

import pytest
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone # Necesario para crear usuario

# Importar helper para crear usuarios y obtener tokens
from tests.helpers import create_user_and_get_token
# Importar modelos y schemas necesarios
from models.usuario import Usuario
from schemas.usuario import UsuarioRead

# Importar funciones de seguridad necesarias
from core.security import verify_password, create_access_token, get_password_hash

# --- Importar settings para obtener el prefijo de la API ---
from core.config import settings
API_PREFIX = settings.API_V1_STR

# --- CONSTANTE PARA PREFIJO ESPECÍFICO DEL ROUTER ---
USUARIOS_PREFIX = f"{API_PREFIX}/usuarios" # ej: /api/v1/usuarios
AUTH_PREFIX = f"{API_PREFIX}/auth"     # ej: /api/v1/auth


# Datos de prueba para un usuario válido
valid_user_data = {
    "username": "testuser_nuevo",
    "email": "test_nuevo@example.com",
    "nombre_completo": "Usuario De Prueba Nuevo",
    "password": "password123", # Contraseña en texto plano para la creación
    "rol": "OPERADOR",
    "activo": True
}
# --- Prueba de creación exitosa ---
@pytest.mark.asyncio
async def test_crear_usuario_exitoso(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba la creación exitosa de un usuario a través de POST /usuarios/
    Verifica el código de estado, la respuesta y el estado en la base de datos (incluyendo hash).
    """
    # --- Ejecución ---
    # --- URL CORREGIDA ---
    url_crear = f"{USUARIOS_PREFIX}/"
    response = await client.post(url_crear, json=valid_user_data)

    # --- Verificación de la Respuesta HTTP ---
    assert response.status_code == status.HTTP_201_CREATED, \
        f"Status esperado 201, obtenido {response.status_code}: {response.text}"

    data = response.json()

    assert "id" in data
    assert data["username"] == valid_user_data["username"]
    assert data["email"] == valid_user_data["email"]
    assert data["nombre_completo"] == valid_user_data["nombre_completo"]
    assert data["rol"] == valid_user_data["rol"]
    assert data["activo"] == valid_user_data["activo"]
    assert "password" not in data
    assert "password_hash" not in data

    # --- Verificación en la Base de Datos ---
    user_id = uuid.UUID(data["id"])
    user_db = await db_session.get(Usuario, user_id)

    assert user_db is not None, "El usuario no fue encontrado en la base de datos."
    assert user_db.username == valid_user_data["username"]
    assert user_db.email == valid_user_data["email"]

    # --- Verificación Crucial del Hash de Contraseña ---
    assert user_db.hashed_password is not None, "El hash de la contraseña no debería ser nulo en la BD."
    assert isinstance(user_db.hashed_password, str), "El hash debería ser un string."
    assert len(user_db.hashed_password) > 0, "El hash no debería estar vacío."
    assert verify_password(valid_user_data["password"], user_db.hashed_password), \
        "La contraseña guardada (hash) no coincide con la contraseña original."
    assert user_db.hashed_password != valid_user_data["password"], \
        "¡Peligro! La contraseña parece estar guardada en texto plano en lugar de hash."

# --- Prueba: Username Duplicado ---
@pytest.mark.asyncio
async def test_crear_usuario_username_duplicado(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que la API devuelve 409 si se intenta crear un usuario con un username existente.
    """
    # 1. Crear un usuario inicial
    initial_user_data = {
        "username": "test_duplicado_user",
        "email": "original_user@example.com",
        "password": "password123"
    }
    # --- URL CORREGIDA ---
    url_crear = f"{USUARIOS_PREFIX}/"
    response_initial = await client.post(url_crear, json=initial_user_data)
    assert response_initial.status_code == status.HTTP_201_CREATED, "Fallo al crear usuario inicial para test duplicado"

    # 2. Intentar crear OTRO usuario con el MISMO username
    duplicate_user_data = {
        "username": "test_duplicado_user", # <-- Username duplicado
        "email": "duplicado_user@example.com",
        "password": "password456"
    }
    # --- URL CORREGIDA ---
    response_duplicate = await client.post(url_crear, json=duplicate_user_data)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_duplicate.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (username duplicado), obtenido {response_duplicate.status_code}: {response_duplicate.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_duplicate.json()
    assert "detail" in data
    assert 'Ya existe un usuario con este nombre de usuario.' in data["detail"]

# --- Prueba: Email Duplicado ---
@pytest.mark.asyncio
async def test_crear_usuario_email_duplicado(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que la API devuelve 409 si se intenta crear un usuario con un email existente.
    """
    # 1. Crear un usuario inicial
    initial_user_data = {
        "username": "original_email_user",
        "email": "test_duplicado_email@example.com", # Email que vamos a duplicar
        "password": "password123"
    }
    # --- URL CORREGIDA ---
    url_crear = f"{USUARIOS_PREFIX}/"
    response_initial = await client.post(url_crear, json=initial_user_data)
    assert response_initial.status_code == status.HTTP_201_CREATED, "Fallo al crear usuario inicial para test email duplicado"

    # 2. Intentar crear OTRO usuario con el MISMO email
    duplicate_user_data = {
        "username": "duplicado_email_user",
        "email": "test_duplicado_email@example.com", # <-- Email duplicado
        "password": "password456"
    }
    # --- URL CORREGIDA ---
    response_duplicate = await client.post(url_crear, json=duplicate_user_data)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_duplicate.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (email duplicado), obtenido {response_duplicate.status_code}: {response_duplicate.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_duplicate.json()
    assert "detail" in data
    assert 'Ya existe un usuario con este email.' in data["detail"]

# --- Prueba: Obtener Usuario Actual (/me) ---
@pytest.mark.asyncio
async def test_read_users_me(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba el endpoint GET /usuarios/me/ para obtener el usuario autenticado.
    """
    # 1. Crear un usuario de prueba directamente en la BD
    user_password = "password_me"
    hashed_password_me = get_password_hash(user_password)
    user_me = Usuario(
        username="test_user_for_me",
        email="me_test@example.com",
        hashed_password=hashed_password_me,
        activo=True,
        rol="OPERADOR",
        creado_en=datetime.now(timezone.utc) # Añadir timestamp
    )
    db_session.add(user_me)
    await db_session.commit()
    await db_session.refresh(user_me)
    user_id_me = user_me.id

    # 2. Obtener un token para este usuario
    login_data = {"username": user_me.username, "password": user_password}
    # --- URL Token OK ---
    response_token = await client.post(f"{AUTH_PREFIX}/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, \
        f"Fallo al obtener token para /me: {response_token.text}"
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Llamar al endpoint GET /usuarios/me/ con el token
    # --- URL /me CORREGIDA ---
    response_me = await client.get(f"{USUARIOS_PREFIX}/me/", headers=headers)

    # 4. Verificar la respuesta
    assert response_me.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 para /me, obtenido {response_me.status_code}: {response_me.text}"
    me_data = response_me.json()

    assert me_data["id"] == str(user_id_me)
    assert me_data["username"] == user_me.username
    assert me_data["email"] == user_me.email

# --- Prueba: Listar Usuarios (GET /) (CORREGIDA) ---
@pytest.mark.asyncio
async def test_read_users(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba el endpoint GET /usuarios/ para obtener la lista de usuarios.
    """
    # 1. Crear un usuario administrador directamente en la base de datos
    from models.usuario import Usuario
    from core.security import get_password_hash
    import uuid
    from datetime import datetime, timezone
    
    # Crear usuario administrador directamente
    admin_id_uuid = uuid.uuid4()
    admin_username = f"admin_test_{uuid.uuid4().hex[:6]}"
    admin_user = Usuario(
        id=admin_id_uuid,
        username=admin_username,
        email=f"{admin_username}@example.com",
        nombre_completo="Admin Test",
        hashed_password=get_password_hash("password123"),
        es_superusuario=True,  # Establecer como superusuario
        activo=True,
        creado_en=datetime.now(timezone.utc),
        actualizado_en=datetime.now(timezone.utc)
    )
    
    # Guardar en la base de datos
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)
    
    print(f"Admin user ID: {admin_user.id}")
    print(f"Admin user es_superusuario: {admin_user.es_superusuario}")
    
    # 2. Obtener token de autenticación para el admin
    login_data = {"username": admin_username, "password": "password123"}
    response_token = await client.post(f"{AUTH_PREFIX}/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, f"Error al obtener token: {response_token.text}"
    
    token = response_token.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Llamar al endpoint para listar usuarios usando el token del administrador
    response = await client.get(f"{USUARIOS_PREFIX}/", headers=admin_headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    assert response.status_code == status.HTTP_200_OK, f"Error al listar usuarios: {response.text}"
    
    # 4. Verificar que la respuesta contiene usuarios
    usuarios_response = response.json()
    print(f"Usuarios response: {usuarios_response}")
    assert isinstance(usuarios_response, list), "La respuesta debe ser una lista"
    assert len(usuarios_response) > 0, "La lista de usuarios no debe estar vacía"
    
    # 5. Verificar que el rol está correctamente asignado
    for usuario in usuarios_response:
        if usuario["username"] == admin_username:
            assert usuario["rol"] == "ADMIN", f"El usuario administrador debería tener rol ADMIN, pero tiene {usuario.get('rol', 'NO_ROLE')}"
            print(f"Usuario admin tiene rol: {usuario.get('rol', 'NO_ROLE')}")
            break
    
    # 5. Verificar que cada usuario tiene los campos requeridos
    for usuario in usuarios_response:
        # Verificar campos obligatorios
        assert "id" in usuario, "El usuario debe tener un ID"
        assert "username" in usuario, "El usuario debe tener un username"
        assert "email" in usuario, "El usuario debe tener un email"
        assert "rol" in usuario, "El usuario debe tener un rol"
    
    # El test pasa si llegamos hasta aquí sin errores
    assert True

# --- Prueba: Obtener Usuario por ID (Éxito) ---
@pytest.mark.asyncio
async def test_read_user_by_id_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba el endpoint GET /usuarios/{user_id} para obtener un usuario existente.
    """
    # 1. Crear un usuario de prueba con rol ADMIN usando el helper
    user_id_get_str, headers = await create_user_and_get_token(client, db_session, "get_id_user", rol="ADMIN", es_superusuario=True)

    # 2. Obtener el objeto Usuario de la BD para verificar username
    user_get = await db_session.get(Usuario, uuid.UUID(user_id_get_str))
    assert user_get is not None

    # headers ya obtenidos del usuario ADMIN

    # --- URL GET por ID CORREGIDA ---
    response = await client.get(f"{USUARIOS_PREFIX}/{user_id_get_str}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id_get_str
    assert data["username"] == user_get.username

# --- Prueba: Obtener Usuario por ID (No Encontrado) ---
@pytest.mark.asyncio
async def test_read_user_by_id_not_found(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /usuarios/{user_id} inexistente -> 404."""
    # 1. Crear un usuario de prueba con rol ADMIN usando el helper
    _, headers = await create_user_and_get_token(client, db_session, "get_404_auth", rol="ADMIN", es_superusuario=True)

    # headers ya obtenidos del usuario ADMIN

    non_existent_id = uuid.uuid4()
    # --- URL GET por ID CORREGIDA ---
    response = await client.get(f"{USUARIOS_PREFIX}/{non_existent_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # ... (verificación detalle) ...

@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba actualización exitosa PUT /usuarios/{user_id}."""
    # 1. Crear un usuario de prueba con rol ADMIN usando el helper
    user_id_to_update_str, headers = await create_user_and_get_token(client, db_session, "update_user", rol="ADMIN")

    # 2. Obtener el objeto Usuario de la BD para verificar
    user_to_update = await db_session.get(Usuario, uuid.UUID(user_id_to_update_str))
    assert user_to_update is not None

    # headers ya obtenidos del usuario ADMIN

    update_payload = {"nombre_completo": "Nombre Actualizado", "email": "updated_me@example.com", "rol": "ADMIN", "activo": False} # username eliminado
    # --- URL PUT CORREGIDA ---
    response = await client.put(f"{USUARIOS_PREFIX}/{user_id_to_update_str}", json=update_payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre_completo"] == update_payload["nombre_completo"]
    assert data["email"] == update_payload["email"]

    await db_session.refresh(user_to_update)
    assert user_to_update.nombre_completo == update_payload["nombre_completo"]
    assert user_to_update.email == update_payload["email"]

# --- PRUEBA: Eliminar Usuario (Lógico) (CORREGIDA) ---
@pytest.mark.asyncio
async def test_delete_user_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba eliminación lógica DELETE /usuarios/{user_id}."""
    # 1. Crear un usuario de prueba con rol ADMIN usando el helper
    user_id_admin, headers = await create_user_and_get_token(client, db_session, "admin_delete", rol="ADMIN", es_superusuario=True)
    
    # 2. Crear un usuario para eliminar
    user_to_delete_data = {
        "username": "user_to_delete",
        "email": "delete_me@example.com",
        "nombre_completo": "Usuario Para Eliminar",
        "password": "password123",
        "rol": "OPERADOR",
        "activo": True
    }
    
    # Crear el usuario que será eliminado
    url_crear = f"{USUARIOS_PREFIX}/"
    response_create = await client.post(url_crear, json=user_to_delete_data, headers=headers)
    assert response_create.status_code == status.HTTP_201_CREATED
    
    user_id_to_delete = response_create.json()["id"]
    
    # 3. Eliminar el usuario (eliminación lógica)
    url_delete = f"{USUARIOS_PREFIX}/{user_id_to_delete}"
    response_delete = await client.delete(url_delete, headers=headers)
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT
    
    # 4. Verificar que el usuario está marcado como inactivo en la base de datos
    user_deleted = await db_session.get(Usuario, uuid.UUID(user_id_to_delete))
    assert user_deleted is not None, "El usuario debería existir en la base de datos"
    assert user_deleted.activo is False, "El usuario debería estar marcado como inactivo"
