# tests/test_fabricantes_neumatico.py
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# Importar modelos, schemas y helpers necesarios
from models.usuario import Usuario
from models.fabricante import FabricanteNeumatico # Modelo a probar
from schemas.fabricante import FabricanteNeumaticoRead, FabricanteNeumaticoUpdate # Schemas
from core.security import get_password_hash, verify_password # Para helper de auth

# --- Helper para Usuario/Token específico para pruebas de Fabricantes ---
async def create_user_and_get_token_for_fabr_tests(
    client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
    """Crea un usuario único para tests de fabricantes y devuelve ID y headers."""
    user_password = f"password_fabr_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_fabr_{user_suffix}"
    email = f"fabr_{user_suffix}@example.com"

    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user = (await db_session.exec(stmt_user)).first()
    user: Usuario
    if not existing_user:
        user = Usuario(
            username=username, email=email, password_hash=hashed_password, activo=True, rol="ADMIN" # Rol para gestionar catálogos
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        user_id = str(user.id)
    else:
        # Asegurarse de que el hash coincida si el usuario ya existe
        if not verify_password(user_password, existing_user.password_hash or ""):
             existing_user.password_hash = hashed_password
             db_session.add(existing_user)
             await db_session.commit()
             await db_session.refresh(existing_user)
        user_id = str(existing_user.id)
        user = existing_user # Usar el usuario existente para el login

    # --- OBTENCIÓN DE TOKEN ---
    login_data = {"username": user.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    if response_token.status_code != status.HTTP_200_OK:
         pytest.fail(
             f"Fallo al obtener token en helper fabr_tests para user {user.username}: "
             f"{response_token.status_code} {response_token.text}. "
             f"Verifica el endpoint /auth/token y la lógica de contraseñas."
         )
    # --- FIN OBTENCIÓN DE TOKEN ---

    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return user_id, headers
# --- Fin Helper ---

# --- Pruebas Existentes ---
@pytest.mark.asyncio
async def test_crear_leer_desactivar_fabricante(client: AsyncClient, db_session: AsyncSession):
    """Prueba el ciclo básico Crear, Leer, Desactivar(Lógico) para un fabricante."""
    # Preparación: Obtener token
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "crud_fabr")
    user_uuid = uuid.UUID(user_id)

    # 1. Crear fabricante
    nombre_fabricante = f"Fabricante CRUD Test {uuid.uuid4()}"
    codigo_fabricante = f"FAB-{uuid.uuid4().hex[:6].upper()}" # Código único
    fabricante_data = {
        "nombre": nombre_fabricante,
        "codigo_abreviado": codigo_fabricante,
        "pais_origen": "Peru",
        "activo": True
    }
    response = await client.post("/fabricantes/", json=fabricante_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Status Crear Fabricante: {response.status_code} {response.text}"
    created_data = response.json()
    fabricante_id = created_data["id"]
    fabricante_id_uuid = uuid.UUID(fabricante_id)

    assert created_data["nombre"] == nombre_fabricante
    assert created_data["codigo_abreviado"] == codigo_fabricante
    assert created_data["pais_origen"] == fabricante_data["pais_origen"]
    assert created_data["activo"] is True

    # 2. Leer fabricante creado
    response_get = await client.get(f"/fabricantes/{fabricante_id}", headers=headers)
    assert response_get.status_code == status.HTTP_200_OK, f"Status Leer Fabricante: {response_get.status_code} {response_get.text}"
    read_data = response_get.json()
    assert read_data["id"] == fabricante_id
    assert read_data["nombre"] == nombre_fabricante

    # 3. Desactivación lógica
    response_delete = await client.delete(f"/fabricantes/{fabricante_id}", headers=headers)
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT, f"Status Delete Fabricante: {response_delete.status_code} {response_delete.text}"

    # 4. Verificar inactivo en BD
    await db_session.commit() # Asegurar que la transacción se cierra antes de leer de nuevo
    db_fabricante = await db_session.get(FabricanteNeumatico, fabricante_id_uuid)
    assert db_fabricante is not None
    assert not db_fabricante.activo
    assert db_fabricante.actualizado_en is not None
    assert db_fabricante.actualizado_por == user_uuid

    # 5. Verificar que no aparece en la lista de activos
    response_activos = await client.get("/fabricantes/", params={"activo": True}, headers=headers)
    assert response_activos.status_code == status.HTTP_200_OK
    lista_activos = response_activos.json()
    ids_activos = {f["id"] for f in lista_activos}
    assert fabricante_id not in ids_activos

    # 6. Verificar que sí aparece en la lista de inactivos
    response_inactivos = await client.get("/fabricantes/", params={"activo": False}, headers=headers)
    assert response_inactivos.status_code == status.HTTP_200_OK
    lista_inactivos = response_inactivos.json()
    ids_inactivos = {f["id"] for f in lista_inactivos}
    assert fabricante_id in ids_inactivos

@pytest.mark.asyncio
async def test_crear_fabricante_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que la API devuelve 409 si se intenta crear un fabricante con un nombre existente.
    """
    # 1. Preparación: Obtener token y crear un fabricante inicial
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "dup_nom_fabr")
    nombre_duplicado = f"Fabricante Nombre Dup Test {uuid.uuid4()}"
    codigo_1 = f"FND1-{uuid.uuid4().hex[:5].upper()}" # Código único 1
    codigo_2 = f"FND2-{uuid.uuid4().hex[:5].upper()}" # Código único 2

    fab_data_1 = {
        "nombre": nombre_duplicado,
        "codigo_abreviado": codigo_1,
    }
    response_1 = await client.post("/fabricantes/", json=fab_data_1, headers=headers)
    assert response_1.status_code == status.HTTP_201_CREATED, "Fallo al crear fabricante inicial"

    # 2. Intentar crear OTRO fabricante con el MISMO nombre
    fab_data_2 = {
        "nombre": nombre_duplicado, # <-- Nombre duplicado
        "codigo_abreviado": codigo_2, # <-- Código diferente y único
    }
    response_2 = await client.post("/fabricantes/", json=fab_data_2, headers=headers)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_2.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (nombre duplicado), obtenido {response_2.status_code}: {response_2.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_2.json()
    assert "detail" in data
    expected_detail_simple = f"Ya existe un fabricante con el nombre '{nombre_duplicado}'"
    expected_detail_complex = f"Conflicto al guardar. El nombre '{nombre_duplicado}' ya podría existir (insensible a mayúsculas/acentos) o hubo otro problema."
    assert data["detail"] == expected_detail_simple or expected_detail_complex in data["detail"], \
           f"Mensaje de error inesperado: {data['detail']}"

@pytest.mark.asyncio
async def test_crear_fabricante_duplicado_codigo(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que la API devuelve 409 si se intenta crear un fabricante con un codigo_abreviado existente.
    """
    # 1. Preparación: Obtener token y crear un fabricante inicial
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "dup_cod_fabr")
    nombre_1 = f"Fabricante Cod Dup 1 {uuid.uuid4()}" # Nombre único 1
    nombre_2 = f"Fabricante Cod Dup 2 {uuid.uuid4()}" # Nombre único 2
    codigo_duplicado = f"FCD-{uuid.uuid4().hex[:6].upper()}" # Código que se duplicará

    fab_data_1 = {
        "nombre": nombre_1,
        "codigo_abreviado": codigo_duplicado,
    }
    response_1 = await client.post("/fabricantes/", json=fab_data_1, headers=headers)
    assert response_1.status_code == status.HTTP_201_CREATED, "Fallo al crear fabricante inicial (cod dup test)"

    # 2. Intentar crear OTRO fabricante con el MISMO codigo_abreviado
    fab_data_2 = {
        "nombre": nombre_2, # <-- Nombre diferente y único
        "codigo_abreviado": codigo_duplicado, # <-- Código duplicado
    }
    response_2 = await client.post("/fabricantes/", json=fab_data_2, headers=headers)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_2.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (código duplicado), obtenido {response_2.status_code}: {response_2.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_2.json()
    assert "detail" in data
    expected_detail_simple = f"Ya existe un fabricante con el código '{codigo_duplicado}'"
    expected_detail_complex = "Conflicto al guardar. El nombre o código ya podría existir (verificar mayúsculas/acentos si aplica) o hubo otro problema."
    assert data["detail"] == expected_detail_simple or expected_detail_complex in data["detail"], \
           f"Mensaje de error inesperado: {data['detail']}"

# --- NUEVAS PRUEBAS ---

@pytest.mark.asyncio
async def test_leer_fabricante_not_found(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba GET /fabricantes/{id} para un ID que no existe.
    Debería devolver 404 Not Found.
    """
    # 1. Preparación: Obtener token y generar ID inexistente
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "get_404_fabr")
    non_existent_uuid = uuid.uuid4()

    # 2. Ejecutar la petición GET
    response = await client.get(f"/fabricantes/{non_existent_uuid}", headers=headers)

    # 3. Verificar 404
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 (Not Found), obtenido {response.status_code}: {response.text}"
    data = response.json()
    assert "detail" in data
    expected_detail = f"Fabricante con ID {non_existent_uuid} no encontrado."
    assert data["detail"] == expected_detail

@pytest.mark.asyncio
async def test_actualizar_fabricante_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba la actualización exitosa de un fabricante via PUT /fabricantes/{id}.
    """
    # 1. Preparación: Crear un fabricante inicial
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "update_fabr")
    user_uuid = uuid.UUID(user_id)
    nombre_original = f"Fabricante Original PUT {uuid.uuid4()}"
    codigo_original = f"ORI-{uuid.uuid4().hex[:6].upper()}"
    fab_inicial_data = {
        "nombre": nombre_original,
        "codigo_abreviado": codigo_original,
        "pais_origen": "Chile",
        "activo": True
    }
    response_create = await client.post("/fabricantes/", json=fab_inicial_data, headers=headers)
    assert response_create.status_code == status.HTTP_201_CREATED, "Fallo al crear fabricante inicial para actualizar"
    created_data = response_create.json()
    fabricante_id = created_data["id"]
    fabricante_id_uuid = uuid.UUID(fabricante_id)

    # 2. Definir los datos para la actualización
    nombre_nuevo = f"Fabricante Actualizado PUT {uuid.uuid4()}"
    codigo_nuevo = f"UPD-{uuid.uuid4().hex[:6].upper()}"
    sitio_web_nuevo = "https://updated.example.com"
    update_payload = {
        "nombre": nombre_nuevo,
        "codigo_abreviado": codigo_nuevo,
        "pais_origen": "Argentina",
        "sitio_web": sitio_web_nuevo,
        "activo": False # Cambiar estado
    }

    # 3. Ejecutar la petición PUT
    response_update = await client.put(
        f"/fabricantes/{fabricante_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar la Respuesta HTTP
    assert response_update.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 OK para PUT, obtenido {response_update.status_code}: {response_update.text}"
    updated_response_data = response_update.json()

    # Verificar que la respuesta contenga los datos actualizados
    assert updated_response_data["id"] == fabricante_id
    assert updated_response_data["nombre"] == nombre_nuevo
    assert updated_response_data["codigo_abreviado"] == codigo_nuevo
    assert updated_response_data["pais_origen"] == update_payload["pais_origen"]
    assert updated_response_data["sitio_web"] == sitio_web_nuevo
    assert updated_response_data["activo"] == update_payload["activo"]
    assert "actualizado_en" in updated_response_data and updated_response_data["actualizado_en"] is not None

    # 5. Verificar directamente en la Base de Datos
    await db_session.commit() # Asegurar cierre de transacción
    db_fab_updated = await db_session.get(FabricanteNeumatico, fabricante_id_uuid)
    assert db_fab_updated is not None
    assert db_fab_updated.nombre == nombre_nuevo
    assert db_fab_updated.codigo_abreviado == codigo_nuevo
    assert db_fab_updated.pais_origen == update_payload["pais_origen"]
    assert db_fab_updated.sitio_web == sitio_web_nuevo
    assert db_fab_updated.activo == update_payload["activo"]
    assert db_fab_updated.actualizado_en is not None
    assert db_fab_updated.actualizado_por == user_uuid

@pytest.mark.asyncio
async def test_actualizar_fabricante_not_found(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /fabricantes/{id} para un ID que no existe.
    Debería devolver 404 Not Found.
    """
    # 1. Preparación: Obtener token y generar ID inexistente
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "put_404_fabr")
    non_existent_uuid = uuid.uuid4()

    update_payload = {"nombre": "Fantasma Actualizado"}

    # 2. Ejecutar la petición PUT
    response = await client.put(
        f"/fabricantes/{non_existent_uuid}",
        json=update_payload,
        headers=headers
    )

    # 3. Verificar 404
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 (Not Found) para PUT ID inexistente, obtenido {response.status_code}: {response.text}"
    data = response.json()
    assert "detail" in data
    expected_detail = f"Fabricante con ID {non_existent_uuid} no encontrado para actualizar."
    assert data["detail"] == expected_detail

@pytest.mark.asyncio
async def test_actualizar_fabricante_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /fabricantes/{id} intentando asignar un nombre que ya existe en otro.
    Debería devolver 409 Conflict.
    """
    # 1. Preparación: Crear dos fabricantes
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "put_dup_nom_fabr")
    nombre_existente = f"Nombre Existente PUT Fab {uuid.uuid4()}"
    codigo_a = f"PUTA-{uuid.uuid4().hex[:5].upper()}"
    codigo_b = f"PUTB-{uuid.uuid4().hex[:5].upper()}"
    nombre_original_b = f"Nombre Original B Fab {uuid.uuid4()}"

    # Fabricante A (cuyo nombre usaremos)
    fab_a_data = {"nombre": nombre_existente, "codigo_abreviado": codigo_a}
    response_a = await client.post("/fabricantes/", json=fab_a_data, headers=headers)
    assert response_a.status_code == status.HTTP_201_CREATED, "Fallo al crear Fab A"

    # Fabricante B (el que actualizaremos)
    fab_b_data = {"nombre": nombre_original_b, "codigo_abreviado": codigo_b}
    response_b = await client.post("/fabricantes/", json=fab_b_data, headers=headers)
    assert response_b.status_code == status.HTTP_201_CREATED, "Fallo al crear Fab B"
    fabricante_b_id = response_b.json()["id"]

    # 2. Intentar actualizar B con el nombre de A
    update_payload = {"nombre": nombre_existente}

    # 3. Ejecutar PUT sobre B
    response_update = await client.put(
        f"/fabricantes/{fabricante_b_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar 409
    assert response_update.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 para PUT con nombre duplicado, obtenido {response_update.status_code}: {response_update.text}"
    data = response_update.json()
    assert "detail" in data
    # Mensaje del router fabricantes_neumatico.py al detectar duplicado en PUT
    expected_detail = f"Nombre '{nombre_existente}' ya existe."
    assert data["detail"] == expected_detail

@pytest.mark.asyncio
async def test_actualizar_fabricante_duplicado_codigo(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /fabricantes/{id} intentando asignar un código que ya existe en otro.
    Debería devolver 409 Conflict.
    """
    # 1. Preparación: Crear dos fabricantes
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "put_dup_cod_fabr")

    # --- CORRECCIÓN AQUÍ: Acortar el código a 10 caracteres o menos ---
    # Usamos [:4] -> CODEX-XXXX (10 caracteres)
    codigo_existente = f"CODEX-{uuid.uuid4().hex[:4].upper()}"
    # -------------------------------------------------------------

    nombre_a = f"Nombre A PUT Cod {uuid.uuid4()}"
    nombre_b_original = f"Nombre B PUT Cod Orig {uuid.uuid4()}"

    # --- CORRECCIÓN AQUÍ: Generar código B original también válido ---
    # Usamos [:6] -> COD-XXXXXX (10 caracteres)
    codigo_b_original = f"COD-{uuid.uuid4().hex[:6].upper()}"
    # -------------------------------------------------------------


    # Fabricante A (cuyo código usaremos)
    fab_a_data = {"nombre": nombre_a, "codigo_abreviado": codigo_existente}
    response_a = await client.post("/fabricantes/", json=fab_a_data, headers=headers)
    # Ahora esta aserción debería pasar (esperamos 201)
    assert response_a.status_code == status.HTTP_201_CREATED, f"Fallo al crear Fab A (PUT Cod Dup): {response_a.text}"

    # Fabricante B (el que actualizaremos)
    fab_b_data = {"nombre": nombre_b_original, "codigo_abreviado": codigo_b_original}
    response_b = await client.post("/fabricantes/", json=fab_b_data, headers=headers)
    assert response_b.status_code == status.HTTP_201_CREATED, f"Fallo al crear Fab B (PUT Cod Dup): {response_b.text}"
    fabricante_b_id = response_b.json()["id"]

    # 2. Intentar actualizar B con el código de A
    update_payload = {"codigo_abreviado": codigo_existente}

    # 3. Ejecutar PUT sobre B
    response_update = await client.put(
        f"/fabricantes/{fabricante_b_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar 409 (Esta es la aserción principal de la prueba)
    assert response_update.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 para PUT con código duplicado, obtenido {response_update.status_code}: {response_update.text}"
    data = response_update.json()
    assert "detail" in data
    # Mensaje del router fabricantes_neumatico.py al detectar duplicado en PUT
    expected_detail = f"Código '{codigo_existente}' ya existe."
    assert data["detail"] == expected_detail

# --- Fin de las pruebas para fabricantes ---