# tests/test_proveedores.py
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# Importar modelos, schemas y helpers necesarios
from models.usuario import Usuario
from models.proveedor import Proveedor # Modelo a probar
from schemas.proveedor import ProveedorRead # Schema de respuesta
from schemas.common import TipoProveedorEnum # Enum para el tipo
from core.security import get_password_hash # Para helper de auth
from schemas.proveedor import ProveedorUpdate, ProveedorRead


# --- Helper para Usuario/Token específico para pruebas de Proveedores ---
# (Similar a los helpers en otros tests)
async def create_user_and_get_token_for_prov_tests(
    client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
    """Crea un usuario único para tests de proveedores y devuelve su ID y headers con token."""
    user_password = f"password_prov_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_prov_{user_suffix}"
    email = f"prov_{user_suffix}@example.com"

    # Verificar si ya existe o crear uno nuevo
    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user = (await db_session.exec(stmt_user)).first()
    if not existing_user:
        user = Usuario(
            username=username, email=email, password_hash=hashed_password, activo=True, rol="ADMIN" # Asumir ADMIN para gestionar catálogos
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        user_id = str(user.id)
    else:
        # Si existe, actualiza el hash por si acaso y obtén el ID
        existing_user.password_hash = hashed_password
        db_session.add(existing_user)
        await db_session.commit()
        await db_session.refresh(existing_user)
        user_id = str(existing_user.id)
        user = existing_user # Usar el usuario existente para el login

    # Obtener token
    login_data = {"username": user.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    if response_token.status_code != status.HTTP_200_OK:
         pytest.fail(f"Fallo al obtener token en helper prov_tests para user {user.username}: {response_token.status_code} {response_token.text}")
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return user_id, headers
# --- Fin Helper ---

# --- Pruebas ---
@pytest.mark.asyncio
async def test_crear_leer_desactivar_proveedor(client: AsyncClient, db_session: AsyncSession):
    """Prueba el ciclo básico Crear, Leer, Desactivar(Lógico) para un proveedor."""
    # Preparación: Obtener token
    user_id, headers = await create_user_and_get_token_for_prov_tests(client, db_session, "crud_prov")

    # 1. Crear proveedor
    nombre_proveedor = f"Proveedor CRUD Test {uuid.uuid4()}"
    proveedor_data = {
        "nombre": nombre_proveedor,
        "tipo": TipoProveedorEnum.DISTRIBUIDOR.value, # Usar el valor del enum
        "rfc": f"CRU-{uuid.uuid4().hex[:9].upper()}",
        "activo": True
    }
    response = await client.post("/proveedores/", json=proveedor_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Status Crear Proveedor: {response.status_code} {response.text}"
    created_data = response.json()
    proveedor_id = created_data["id"]
    proveedor_id_uuid = uuid.UUID(proveedor_id)

    assert created_data["nombre"] == nombre_proveedor
    assert created_data["tipo"] == proveedor_data["tipo"]
    assert created_data["rfc"] == proveedor_data["rfc"]
    assert created_data["activo"] is True

    # 2. Leer proveedor creado
    response = await client.get(f"/proveedores/{proveedor_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"Status Leer Proveedor: {response.status_code} {response.text}"
    read_data = response.json()
    assert read_data["id"] == proveedor_id
    assert read_data["nombre"] == nombre_proveedor

    # 3. Desactivación lógica
    response = await client.delete(f"/proveedores/{proveedor_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Status Delete Proveedor: {response.status_code}"

    # 4. Verificar inactivo en BD
    db_proveedor = await db_session.get(Proveedor, proveedor_id_uuid)
    assert db_proveedor is not None
    assert not db_proveedor.activo
    assert db_proveedor.actualizado_en is not None
    assert db_proveedor.actualizado_por == uuid.UUID(user_id)

    # 5. Verificar que no aparece en la lista de activos
    response_activos = await client.get("/proveedores/", params={"activo": True}, headers=headers)
    assert response_activos.status_code == status.HTTP_200_OK
    lista_activos = response_activos.json()
    ids_activos = {p["id"] for p in lista_activos}
    assert proveedor_id not in ids_activos

    # 6. Verificar que sí aparece en la lista de inactivos
    response_inactivos = await client.get("/proveedores/", params={"activo": False}, headers=headers)
    assert response_inactivos.status_code == status.HTTP_200_OK
    lista_inactivos = response_inactivos.json()
    ids_inactivos = {p["id"] for p in lista_inactivos}
    assert proveedor_id in ids_inactivos

# --- NUEVA PRUEBA: Crear Proveedor con Nombre Duplicado ---
@pytest.mark.asyncio
async def test_crear_proveedor_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que la API devuelve 409 si se intenta crear un proveedor con un nombre existente.
    """
    # 1. Preparación: Obtener token y crear un proveedor inicial
    user_id, headers = await create_user_and_get_token_for_prov_tests(client, db_session, "dup_prov")
    nombre_duplicado = f"Proveedor Duplicado Test {uuid.uuid4()}" # Nombre único para esta ejecución de test
    proveedor_data_1 = {
        "nombre": nombre_duplicado,
        "tipo": TipoProveedorEnum.OTRO.value,
        "rfc": f"DUP2-{uuid.uuid4().hex[:8].upper()}", # Cambiar :9 por :8 (5+8=13 chars)
    }
    response_1 = await client.post("/proveedores/", json=proveedor_data_1, headers=headers)
    assert response_1.status_code == status.HTTP_201_CREATED, "Fallo al crear proveedor inicial para test duplicado"

    # 2. Intentar crear OTRO proveedor con el MISMO nombre
     # 2. Intentar crear OTRO proveedor con el MISMO nombre
    proveedor_data_2 = {
        "nombre": nombre_duplicado, # <-- Nombre duplicado
        "tipo": TipoProveedorEnum.DISTRIBUIDOR.value, # Otros datos pueden ser diferentes
        # --- ¡ESTA LÍNEA NECESITA CAMBIARSE! ---
        "rfc": f"DUP2-{uuid.uuid4().hex[:8].upper()}", # Debe ser [:8] para que 5+8=13
        # --------------------------------------
    }
    response_2 = await client.post("/proveedores/", json=proveedor_data_2, headers=headers)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_2.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (nombre duplicado), obtenido {response_2.status_code}: {response_2.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_2.json()
    assert "detail" in data
    # Asegúrate que este mensaje coincida con el que pusiste en routers/proveedores.py
    expected_detail = f"Ya existe un proveedor con el nombre '{nombre_duplicado}'"
    assert data["detail"] == expected_detail

# --- NUEVA PRUEBA: Leer Proveedor No Encontrado (404) ---
@pytest.mark.asyncio
async def test_leer_proveedor_not_found(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba GET /proveedores/{id} para un ID que no existe.
    Debería devolver 404 Not Found.
    """
    # 1. Preparación: Obtener token y generar un ID inexistente
    user_id, headers = await create_user_and_get_token_for_prov_tests(client, db_session, "get_404_prov")
    non_existent_uuid = uuid.uuid4() # UUID aleatorio

    # 2. Ejecutar la petición GET con el ID inexistente
    response = await client.get(f"/proveedores/{non_existent_uuid}", headers=headers)

    # 3. Verificar que la respuesta sea 404 Not Found
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 (Not Found), obtenido {response.status_code}: {response.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response.json()
    assert "detail" in data
    # Asegúrate que este mensaje coincida con el que pusiste en routers/proveedores.py
    expected_detail = f"Proveedor con ID {non_existent_uuid} no encontrado."
    assert data["detail"] == expected_detail

# --- NUEVA PRUEBA: Actualizar Proveedor Exitosamente ---
@pytest.mark.asyncio
async def test_actualizar_proveedor_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba la actualización exitosa de un proveedor via PUT /proveedores/{id}.
    """
    # 1. Preparación: Crear un proveedor inicial
    user_id, headers = await create_user_and_get_token_for_prov_tests(client, db_session, "update_prov")
    nombre_original = f"Proveedor Original {uuid.uuid4()}"
    rfc_original = f"ORI-{uuid.uuid4().hex[:9].upper()}" # 13 chars
    proveedor_inicial_data = {
        "nombre": nombre_original,
        "tipo": TipoProveedorEnum.OTRO.value,
        "rfc": rfc_original,
        "activo": True
    }
    response_create = await client.post("/proveedores/", json=proveedor_inicial_data, headers=headers)
    assert response_create.status_code == status.HTTP_201_CREATED, "Fallo al crear proveedor inicial para actualizar"
    created_data = response_create.json()
    proveedor_id = created_data["id"]
    proveedor_id_uuid = uuid.UUID(proveedor_id)

    # 2. Definir los datos para la actualización
    nombre_nuevo = f"Proveedor Actualizado {uuid.uuid4()}"
    rfc_nuevo = f"UPD-{uuid.uuid4().hex[:9].upper()}" # 13 chars
    update_payload = {
        "nombre": nombre_nuevo,
        "tipo": TipoProveedorEnum.SERVICIO_REPARACION.value, # Cambiar tipo
        "rfc": rfc_nuevo, # Cambiar RFC
        "activo": False, # Cambiar estado
        "contacto_principal": "Contacto Actualizado", # Añadir/cambiar campos opcionales
        "telefono": "987654321"
    }

    # 3. Ejecutar la petición PUT
    response_update = await client.put(
        f"/proveedores/{proveedor_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar la Respuesta HTTP
    assert response_update.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 OK para PUT, obtenido {response_update.status_code}: {response_update.text}"
    updated_response_data = response_update.json()

    # Verificar que la respuesta contenga los datos actualizados
    assert updated_response_data["id"] == proveedor_id
    assert updated_response_data["nombre"] == nombre_nuevo
    assert updated_response_data["tipo"] == update_payload["tipo"]
    assert updated_response_data["rfc"] == rfc_nuevo
    assert updated_response_data["activo"] == update_payload["activo"]
    # Verifica también los campos opcionales si tu schema ProveedorRead los incluye
    # assert updated_response_data["contacto_principal"] == update_payload["contacto_principal"]
    # assert updated_response_data["telefono"] == update_payload["telefono"]
    assert "actualizado_en" in updated_response_data and updated_response_data["actualizado_en"] is not None

    # 5. Verificar directamente en la Base de Datos
    db_proveedor_updated = await db_session.get(Proveedor, proveedor_id_uuid)
    assert db_proveedor_updated is not None
    assert db_proveedor_updated.nombre == nombre_nuevo
    assert db_proveedor_updated.tipo.value == update_payload["tipo"] # Compara el valor del Enum
    assert db_proveedor_updated.rfc == rfc_nuevo
    assert db_proveedor_updated.activo == update_payload["activo"]
    assert db_proveedor_updated.contacto_principal == update_payload["contacto_principal"]
    assert db_proveedor_updated.telefono == update_payload["telefono"]
    assert db_proveedor_updated.actualizado_en is not None
    assert db_proveedor_updated.actualizado_por == uuid.UUID(user_id)

# --- NUEVA PRUEBA: Actualizar Proveedor No Encontrado (404) ---
@pytest.mark.asyncio
async def test_actualizar_proveedor_not_found(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /proveedores/{id} para un ID que no existe.
    Debería devolver 404 Not Found.
    """
    # 1. Preparación: Obtener token y generar ID inexistente
    user_id, headers = await create_user_and_get_token_for_prov_tests(client, db_session, "put_404_prov")
    non_existent_uuid = uuid.uuid4() # UUID aleatorio

    # Datos de actualización (el contenido no importa mucho)
    update_payload = {
        "nombre": "Proveedor Fantasma Actualizado",
        "activo": False
    }

    # 2. Ejecutar la petición PUT con el ID inexistente
    response = await client.put(
        f"/proveedores/{non_existent_uuid}",
        json=update_payload,
        headers=headers
    )

    # 3. Verificar que la respuesta sea 404 Not Found
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 (Not Found) para PUT ID inexistente, obtenido {response.status_code}: {response.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response.json()
    assert "detail" in data
    # Asegúrate que este mensaje coincida con el que pusiste en routers/proveedores.py
    expected_detail = f"Proveedor con ID {non_existent_uuid} no encontrado para actualizar."
    assert data["detail"] == expected_detail

# --- NUEVA PRUEBA: Actualizar Proveedor con Nombre Duplicado (409) ---
@pytest.mark.asyncio
async def test_actualizar_proveedor_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /proveedores/{id} intentando asignar un nombre que ya existe en otro proveedor.
    Debería devolver 409 Conflict.
    """
    # 1. Preparación: Crear dos proveedores
    user_id, headers = await create_user_and_get_token_for_prov_tests(client, db_session, "put_dup_prov")
    nombre_existente = f"Nombre Existente PUT {uuid.uuid4()}"
    rfc_valido_1 = f"EXT-{uuid.uuid4().hex[:9].upper()}" # 13 chars
    rfc_valido_2 = f"CHG-{uuid.uuid4().hex[:9].upper()}" # 13 chars

    # Proveedor A (cuyo nombre usaremos como duplicado)
    prov_a_data = {"nombre": nombre_existente, "rfc": rfc_valido_1, "tipo": TipoProveedorEnum.OTRO.value}
    response_a = await client.post("/proveedores/", json=prov_a_data, headers=headers)
    assert response_a.status_code == status.HTTP_201_CREATED, "Fallo al crear Proveedor A"
    proveedor_a_id = response_a.json()["id"]

    # Proveedor B (el que intentaremos actualizar)
    prov_b_data = {"nombre": f"Nombre Original B {uuid.uuid4()}", "rfc": rfc_valido_2, "tipo": TipoProveedorEnum.OTRO.value}
    response_b = await client.post("/proveedores/", json=prov_b_data, headers=headers)
    assert response_b.status_code == status.HTTP_201_CREATED, "Fallo al crear Proveedor B"
    proveedor_b_id = response_b.json()["id"]

    # 2. Definir payload para intentar actualizar B con el nombre de A
    update_payload = {
        "nombre": nombre_existente # <-- Intentando usar el nombre de Proveedor A
        # No es necesario enviar otros campos para esta prueba de conflicto
    }

    # 3. Ejecutar la petición PUT sobre Proveedor B
    response_update = await client.put(
        f"/proveedores/{proveedor_b_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar que la respuesta sea 409 Conflict
    assert response_update.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 para PUT con nombre duplicado, obtenido {response_update.status_code}: {response_update.text}"

    # 5. (Opcional) Verificar el mensaje de detalle del error
    data = response_update.json()
    assert "detail" in data
    # Asegúrate que este mensaje coincida con el que pusiste en routers/proveedores.py
    expected_detail = f"Ya existe otro proveedor con el nombre '{nombre_existente}'"
    assert data["detail"] == expected_detail
# --- Fin de las pruebas para proveedores ---