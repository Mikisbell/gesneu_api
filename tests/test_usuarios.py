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

# --- NUEVA PRUEBA: Obtener Usuario por ID (Éxito) ---
@pytest.mark.asyncio
async def test_read_user_by_id_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba el endpoint GET /usuarios/{user_id} para obtener un usuario existente.
    """
    # 1. Crear un usuario de prueba directamente en la BD
    user_password = "password_get_id"
    hashed_password_get = get_password_hash(user_password)
    user_get = Usuario(
        username="test_user_get_id",
        email="get_id@example.com",
        password_hash=hashed_password_get,
        activo=True,
        rol="OPERADOR"
    )
    db_session.add(user_get)
    await db_session.commit()
    await db_session.refresh(user_get)
    user_id_get = user_get.id # ID del usuario que queremos obtener
    user_id_get_str = str(user_id_get)

    # 2. Obtener un token (necesitamos estar logueados para llamar al endpoint)
    #    Usaremos el mismo usuario para loguearnos y obtener el token
    login_data = {"username": user_get.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, \
        f"Fallo al obtener token para GET by ID: {response_token.text}"
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Llamar al endpoint GET /usuarios/{user_id} con el ID y el token
    response = await client.get(f"/usuarios/{user_id_get_str}", headers=headers)

    # 4. Verificar la respuesta
    assert response.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 para GET by ID, obtenido {response.status_code}: {response.text}"
    data = response.json()

    # Verificar que los datos coinciden con el usuario creado
    assert data["id"] == user_id_get_str
    assert data["username"] == user_get.username
    assert data["email"] == user_get.email

# --- NUEVA PRUEBA: Obtener Usuario por ID (No Encontrado) ---
@pytest.mark.asyncio
async def test_read_user_by_id_not_found(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que GET /usuarios/{user_id} devuelve 404 si el ID no existe.
    """
    # 1. Crear un usuario y obtener token para poder llamar al endpoint
    #    (Necesitamos estar autenticados, aunque el ID que busquemos no exista)
    user_password = "password_get_404"
    hashed_password_404 = get_password_hash(user_password)
    user_auth = Usuario(
        username="test_user_auth_404",
        email="auth_404@example.com",
        password_hash=hashed_password_404
    )
    db_session.add(user_auth)
    await db_session.commit()

    login_data = {"username": user_auth.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Generar un ID aleatorio que (con alta probabilidad) no exista
    non_existent_id = uuid.uuid4()

    # 3. Llamar al endpoint GET /usuarios/{user_id} con el ID inexistente
    response = await client.get(f"/usuarios/{non_existent_id}", headers=headers)

    # 4. Verificar que la respuesta sea 404 Not Found
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 para ID inexistente, obtenido {response.status_code}: {response.text}"

    # 5. (Opcional) Verificar el detalle del error
    data = response.json()
    assert "detail" in data
    assert f"Usuario con ID {non_existent_id} no encontrado" in data["detail"]

@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba la actualización exitosa de un usuario via PUT /usuarios/{user_id}.
    """
    # 1. Crear un usuario inicial directamente en la BD
    user_password = "password_update"
    hashed_password_update = get_password_hash(user_password)
    user_to_update = Usuario(
        username="test_user_to_update",
        email="update_me@example.com",
        nombre_completo="Nombre Original",
        password_hash=hashed_password_update,
        activo=True,
        rol="OPERADOR"
    )
    db_session.add(user_to_update)
    await db_session.commit()
    await db_session.refresh(user_to_update)
    user_id_to_update = user_to_update.id
    user_id_to_update_str = str(user_id_to_update)

    # 2. Obtener un token para este usuario (o un admin si se requieren permisos)
    login_data = {"username": user_to_update.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, \
        f"Fallo al obtener token para PUT: {response_token.text}"
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Definir los datos de actualización
    update_payload = {
        "nombre_completo": "Nombre Actualizado",
        "email": "updated_me@example.com",
        "rol": "ADMIN", # Intentar cambiar el rol
        "activo": False # Intentar desactivar
        # No incluimos password ni username según nuestro schema UsuarioUpdate
    }

    # 4. Llamar al endpoint PUT /usuarios/{user_id}
    response = await client.put(
        f"/usuarios/{user_id_to_update_str}",
        json=update_payload,
        headers=headers
    )

    # 5. Verificar la respuesta HTTP
    assert response.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 para PUT, obtenido {response.status_code}: {response.text}"
    data = response.json()

    # Verificar que la respuesta contenga los datos actualizados
    assert data["id"] == user_id_to_update_str
    assert data["username"] == user_to_update.username # Username no debería cambiar
    assert data["nombre_completo"] == update_payload["nombre_completo"]
    assert data["email"] == update_payload["email"]
    assert data["rol"] == update_payload["rol"]
    assert data["activo"] == update_payload["activo"]
    assert "actualizado_en" in data and data["actualizado_en"] is not None

    # 6. Verificar directamente en la Base de Datos que los cambios se guardaron
    await db_session.refresh(user_to_update) # Refrescar el objeto desde la BD
    assert user_to_update.nombre_completo == update_payload["nombre_completo"]
    assert user_to_update.email == update_payload["email"]
    assert user_to_update.rol == update_payload["rol"]
    assert user_to_update.activo == update_payload["activo"]
    assert user_to_update.actualizado_por == user_to_update.id # Asumiendo que el propio usuario se actualizó
    assert user_to_update.actualizado_en is not None

# tests/test_usuarios.py
# ... (imports y pruebas existentes hasta test_update_user_success) ...


# --- PRUEBA: Eliminar Usuario (Lógico) (CORREGIDA) ---
@pytest.mark.asyncio
async def test_delete_user_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba la eliminación lógica exitosa de un usuario via DELETE /usuarios/{user_id}.
    Verifica el código de estado 204 y que el usuario quede inactivo en la BD.
    """
    # 1. Crear un usuario de prueba directamente en la BD que vamos a eliminar
    user_password = "password_delete"
    hashed_password_delete = get_password_hash(user_password)
    user_to_delete = Usuario(
        username="test_user_to_delete",
        email="delete_me@example.com",
        password_hash=hashed_password_delete,
        activo=True, # Asegurarse que empieza activo
        rol="OPERADOR"
    )
    db_session.add(user_to_delete)
    await db_session.commit()
    await db_session.refresh(user_to_delete)
    user_id_to_delete = user_to_delete.id
    user_id_to_delete_str = str(user_id_to_delete)

    # 2. Obtener un token (el usuario que realiza la acción de borrado)
    #    (Idealmente sería un admin)
    login_data = {"username": user_to_delete.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, \
        f"Fallo al obtener token para DELETE: {response_token.text}"
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Llamar al endpoint DELETE /usuarios/{user_id}
    response = await client.delete(f"/usuarios/{user_id_to_delete_str}", headers=headers)

    # 4. Verificar la respuesta HTTP (204 No Content)
    assert response.status_code == status.HTTP_204_NO_CONTENT, \
        f"Status esperado 204 para DELETE, obtenido {response.status_code}"

    # 5. Verificar directamente en la Base de Datos que el usuario está inactivo
    #    Es importante refrescar ANTES de verificar
    await db_session.refresh(user_to_delete) # Refrescar el estado desde la BD
    assert not user_to_delete.activo, "El usuario debería estar inactivo (activo=False) tras DELETE."
    assert user_to_delete.actualizado_en is not None # Verificar que se actualizó la fecha

    # --- EL PASO 6 OPCIONAL HA SIDO ELIMINADO ---
