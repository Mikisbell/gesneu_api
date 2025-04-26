# tests/test_usuarios.py
import pytest
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession

# Importar modelos y schemas necesarios
from models.usuario import Usuario
from schemas.usuario import UsuarioRead

# Importar funciones de seguridad necesarias
from core.security import verify_password, create_access_token, get_password_hash # Asegúrate que estas 3 estén

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
    response = await client.post("/usuarios/", json=valid_user_data)

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
    assert user_db.password_hash is not None, "El hash de la contraseña no debería ser nulo en la BD."
    assert isinstance(user_db.password_hash, str), "El hash debería ser un string."
    assert len(user_db.password_hash) > 0, "El hash no debería estar vacío."
    assert verify_password(valid_user_data["password"], user_db.password_hash), \
        "La contraseña guardada (hash) no coincide con la contraseña original."
    assert user_db.password_hash != valid_user_data["password"], \
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
    response_initial = await client.post("/usuarios/", json=initial_user_data)
    assert response_initial.status_code == status.HTTP_201_CREATED, "Fallo al crear usuario inicial para test duplicado"

    # 2. Intentar crear OTRO usuario con el MISMO username
    duplicate_user_data = {
        "username": "test_duplicado_user", # <-- Username duplicado
        "email": "duplicado_user@example.com",
        "password": "password456"
    }
    response_duplicate = await client.post("/usuarios/", json=duplicate_user_data)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_duplicate.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (username duplicado), obtenido {response_duplicate.status_code}: {response_duplicate.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_duplicate.json()
    assert "detail" in data
    assert f"El nombre de usuario '{initial_user_data['username']}' ya está registrado" in data["detail"]


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
    response_initial = await client.post("/usuarios/", json=initial_user_data)
    assert response_initial.status_code == status.HTTP_201_CREATED, "Fallo al crear usuario inicial para test email duplicado"

    # 2. Intentar crear OTRO usuario con el MISMO email
    duplicate_user_data = {
        "username": "duplicado_email_user",
        "email": "test_duplicado_email@example.com", # <-- Email duplicado
        "password": "password456"
    }
    response_duplicate = await client.post("/usuarios/", json=duplicate_user_data)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_duplicate.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (email duplicado), obtenido {response_duplicate.status_code}: {response_duplicate.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_duplicate.json()
    assert "detail" in data
    assert f"El email '{initial_user_data['email']}' ya está registrado" in data["detail"]


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
        password_hash=hashed_password_me,
        activo=True,
        rol="OPERADOR"
    )
    db_session.add(user_me)
    await db_session.commit()
    await db_session.refresh(user_me)
    user_id_me = user_me.id

    # 2. Obtener un token para este usuario
    login_data = {"username": user_me.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, \
        f"Fallo al obtener token para /me: {response_token.text}"
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Llamar al endpoint GET /usuarios/me/ con el token
    response_me = await client.get("/usuarios/me/", headers=headers)

    # 4. Verificar la respuesta
    assert response_me.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 para /me, obtenido {response_me.status_code}: {response_me.text}"
    me_data = response_me.json()

    assert me_data["id"] == str(user_id_me)
    assert me_data["username"] == user_me.username
    assert me_data["email"] == user_me.email


# --- Prueba: Listar Usuarios (GET /) (CORREGIDA - SIN DUPLICACIÓN) ---
@pytest.mark.asyncio
async def test_read_users(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba el endpoint GET /usuarios/ para listar usuarios.
    """
    # 1. Crear usuarios de prueba directamente en BD
    user_password_list = "password_list"
    hashed_password_list = get_password_hash(user_password_list)
    user_list1 = Usuario(username="list_user_1", email="list1@example.com", password_hash=hashed_password_list)
    user_list2 = Usuario(username="list_user_2", email="list2@example.com", password_hash=hashed_password_list)
    db_session.add_all([user_list1, user_list2])
    await db_session.commit()
    await db_session.refresh(user_list1)
    await db_session.refresh(user_list2)
    user1_id_str = str(user_list1.id)
    user2_id_str = str(user_list2.id)

    # 2. Obtener token para uno de los usuarios
    login_data = {"username": user_list1.username, "password": user_password_list}
    response_token = await client.post("/auth/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, \
        f"Fallo al obtener token para listar: {response_token.text}"
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Llamar al endpoint GET /usuarios/ con autenticación
    response_list = await client.get("/usuarios/", headers=headers)

    # 4. Verificar la respuesta
    assert response_list.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 para listar, obtenido {response_list.status_code}: {response_list.text}"

    users_list = response_list.json()
    assert isinstance(users_list, list), "La respuesta debería ser una lista"

    # Crear sets de IDs para facilitar la comprobación de presencia
    ids_in_response = {user["id"] for user in users_list}
    assert user1_id_str in ids_in_response, f"Usuario {user1_id_str} no encontrado en la lista"
    assert user2_id_str in ids_in_response, f"Usuario {user2_id_str} no encontrado en la lista"

    # Opcional: Verificar usernames también
    usernames_in_response = {user["username"] for user in users_list}
    assert user_list1.username in usernames_in_response
    assert user_list2.username in usernames_in_response