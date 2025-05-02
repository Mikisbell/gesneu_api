# tests/test_tipos_vehiculo.py
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# Importar modelos, schemas y helpers necesarios
from models.usuario import Usuario
from models.tipo_vehiculo import TipoVehiculo # Modelo a probar
from schemas.tipo_vehiculo import TipoVehiculoRead # Schema de respuesta
from core.security import get_password_hash # Para helper de auth
from schemas.tipo_vehiculo import TipoVehiculoUpdate, TipoVehiculoRead

# --- Helper para Usuario/Token específico para pruebas de Tipos Vehiculo ---
async def create_user_and_get_token_for_tipov_tests(
    client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
    """Crea un usuario único para tests de tipos vehiculo y devuelve ID y headers."""
    user_password = f"password_tipov_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_tipov_{user_suffix}"
    email = f"tipov_{user_suffix}@example.com"

    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user = (await db_session.exec(stmt_user)).first()
    if not existing_user:
        user = Usuario(
            username=username, email=email, password_hash=hashed_password, activo=True, rol="ADMIN" # Rol para gestionar catálogos
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        user_id = str(user.id)
    else:
        existing_user.password_hash = hashed_password
        db_session.add(existing_user)
        await db_session.commit()
        await db_session.refresh(existing_user)
        user_id = str(existing_user.id)
        user = existing_user

    login_data = {"username": user.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    if response_token.status_code != status.HTTP_200_OK:
         pytest.fail(f"Fallo al obtener token en helper tipov_tests para user {user.username}: {response_token.status_code} {response_token.text}")
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return user_id, headers
# --- Fin Helper ---

# --- Pruebas ---
@pytest.mark.asyncio
async def test_crear_leer_desactivar_tipo_vehiculo(client: AsyncClient, db_session: AsyncSession):
    """Prueba el ciclo básico Crear, Leer, Desactivar(Lógico) para un tipo de vehículo."""
    # Preparación: Obtener token
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "crud_tipov")

    # 1. Crear tipo de vehículo
    nombre_tipo_vehiculo = f"Tipo Vehículo CRUD Test {uuid.uuid4()}"
    tipo_vehiculo_data = {
        "nombre": nombre_tipo_vehiculo,
        "ejes_standard": 3, # Valor válido (entre 1 y 10)
        "categoria_principal": "Carga Pesada",
        "activo": True
    }
    response = await client.post("/tipos_vehiculo/", json=tipo_vehiculo_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Status Crear Tipo Vehículo: {response.status_code} {response.text}"
    created_data = response.json()
    tipo_vehiculo_id = created_data["id"]
    tipo_vehiculo_id_uuid = uuid.UUID(tipo_vehiculo_id)

    assert created_data["nombre"] == nombre_tipo_vehiculo
    assert created_data["ejes_standard"] == tipo_vehiculo_data["ejes_standard"]
    assert created_data["categoria_principal"] == tipo_vehiculo_data["categoria_principal"]
    assert created_data["activo"] is True

    # 2. Leer tipo de vehículo creado
    response = await client.get(f"/tipos_vehiculo/{tipo_vehiculo_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"Status Leer Tipo Vehículo: {response.status_code} {response.text}"
    read_data = response.json()
    assert read_data["id"] == tipo_vehiculo_id
    assert read_data["nombre"] == nombre_tipo_vehiculo

    # 3. Desactivación lógica
    response = await client.delete(f"/tipos_vehiculo/{tipo_vehiculo_id}", headers=headers)
    # Manejar posible 409 si tiene dependencias con ON DELETE RESTRICT
    # Por ahora, esperamos 204 si no está en uso. Si falla aquí con 409, la lógica de negocio lo impide.
    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Status Delete Tipo Vehículo: {response.status_code} {response.text}"

    # 4. Verificar inactivo en BD
    db_tipo_vehiculo = await db_session.get(TipoVehiculo, tipo_vehiculo_id_uuid)
    assert db_tipo_vehiculo is not None
    assert not db_tipo_vehiculo.activo
    assert db_tipo_vehiculo.actualizado_en is not None
    assert db_tipo_vehiculo.actualizado_por == uuid.UUID(user_id)

    # 5. Verificar que no aparece en la lista de activos
    response_activos = await client.get("/tipos_vehiculo/", params={"activo": True}, headers=headers)
    assert response_activos.status_code == status.HTTP_200_OK
    lista_activos = response_activos.json()
    ids_activos = {tv["id"] for tv in lista_activos}
    assert tipo_vehiculo_id not in ids_activos

    # 6. Verificar que sí aparece en la lista de inactivos
    response_inactivos = await client.get("/tipos_vehiculo/", params={"activo": False}, headers=headers)
    assert response_inactivos.status_code == status.HTTP_200_OK
    lista_inactivos = response_inactivos.json()
    ids_inactivos = {tv["id"] for tv in lista_inactivos}
    assert tipo_vehiculo_id in ids_inactivos

# --- Aquí añadiremos más pruebas (duplicados, validaciones, etc.) ---
# --- NUEVA PRUEBA: Crear Tipo Vehículo con Nombre Duplicado ---
@pytest.mark.asyncio
async def test_crear_tipo_vehiculo_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que la API devuelve 409 si se intenta crear un tipo de vehículo con un nombre existente.
    """
    # 1. Preparación: Obtener token y crear un tipo de vehículo inicial
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "dup_tipov")
    nombre_duplicado = f"Tipo Vehículo Duplicado {uuid.uuid4()}" # Nombre único para esta ejecución
    tipo_data_1 = {
        "nombre": nombre_duplicado,
        "ejes_standard": 2, # Valor válido
    }
    response_1 = await client.post("/tipos_vehiculo/", json=tipo_data_1, headers=headers)
    assert response_1.status_code == status.HTTP_201_CREATED, "Fallo al crear tipo vehículo inicial"

    # 2. Intentar crear OTRO tipo con el MISMO nombre
    tipo_data_2 = {
        "nombre": nombre_duplicado, # <-- Nombre duplicado
        "ejes_standard": 4, # Otros datos pueden ser diferentes
        "categoria_principal": "Otro"
    }
    response_2 = await client.post("/tipos_vehiculo/", json=tipo_data_2, headers=headers)

    # 3. Verificar que la respuesta sea 409 Conflict
    assert response_2.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (nombre duplicado), obtenido {response_2.status_code}: {response_2.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response_2.json()
    assert "detail" in data
    # El mensaje puede venir del chequeo simple o del IntegrityError, sé flexible
    expected_detail_simple = f"Ya existe un tipo de vehículo con el nombre '{nombre_duplicado}'"
    expected_detail_complex = f"Conflicto al guardar. El nombre '{nombre_duplicado}' ya podría existir (insensible a mayúsculas/acentos) o hubo otro problema."
    assert data["detail"] == expected_detail_simple or expected_detail_complex in data["detail"], \
           f"Mensaje de error inesperado: {data['detail']}"

# --- Aquí añadiremos más pruebas ---
@pytest.mark.asyncio
async def test_crear_tipo_vehiculo_ejes_fuera_rango_min(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que falla al crear un tipo de vehículo con ejes_standard < 1.
    Debería devolver 422 Unprocessable Entity.
    """
    # 1. Preparación: Obtener token
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "ejes_min_tipov")
    nombre_tipo_vehiculo = f"Tipo Vehículo Ejes Min Test {uuid.uuid4()}"

    # 2. Definir payload con valor inválido (menor que 1)
    tipo_vehiculo_data_invalida = {
        "nombre": nombre_tipo_vehiculo,
        "ejes_standard": 0, # <-- Valor inválido (< 1)
    }

    # 3. Ejecutar la petición POST (esperando error 422)
    response = await client.post("/tipos_vehiculo/", json=tipo_vehiculo_data_invalida, headers=headers)

    # 4. Verificar la Respuesta de Error HTTP (422)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, \
        f"Status esperado 422 para ejes < 1, obtenido {response.status_code}: {response.text}"

    # Verificar el detalle del error (Pydantic debe indicar que el valor es menor al mínimo)
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    assert len(data["detail"]) > 0
    # Buscar el error específico para 'ejes_standard'
    error_encontrado = False
    for error in data["detail"]:
        if error.get("loc") == ["body", "ejes_standard"] and error.get("type") == "greater_than_equal":
# ----------------------------
         # El assert del mensaje ya estaba bien:
         assert "Input should be greater than or equal to 1" in error.get("msg", "")
         error_encontrado = True
         break
    assert error_encontrado, f"No se encontró el detalle de error esperado para 'ejes_standard' < 1 en: {data['detail']}"

@pytest.mark.asyncio
async def test_crear_tipo_vehiculo_ejes_fuera_rango_max(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba que falla al crear un tipo de vehículo con ejes_standard > 10.
    Debería devolver 422 Unprocessable Entity.
    """
    # 1. Preparación: Obtener token
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "ejes_max_tipov")
    nombre_tipo_vehiculo = f"Tipo Vehículo Ejes Max Test {uuid.uuid4()}"

    # 2. Definir payload con valor inválido (mayor que 10)
    tipo_vehiculo_data_invalida = {
        "nombre": nombre_tipo_vehiculo,
        "ejes_standard": 11, # <-- Valor inválido (> 10)
    }

    # 3. Ejecutar la petición POST (esperando error 422)
    response = await client.post("/tipos_vehiculo/", json=tipo_vehiculo_data_invalida, headers=headers)

    # 4. Verificar la Respuesta de Error HTTP (422)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, \
        f"Status esperado 422 para ejes > 10, obtenido {response.status_code}: {response.text}"

    # Verificar el detalle del error (Pydantic debe indicar que el valor es mayor al máximo)
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    assert len(data["detail"]) > 0
    # Buscar el error específico para 'ejes_standard'
    error_encontrado = False
    for error in data["detail"]:
       if error.get("loc") == ["body", "ejes_standard"] and error.get("type") == "less_than_equal":
# ----------------------------
         # El assert del mensaje ya estaba bien:
         assert "Input should be less than or equal to 10" in error.get("msg", "")
         error_encontrado = True
         break
    assert error_encontrado, f"No se encontró el detalle de error esperado para 'ejes_standard' > 10 en: {data['detail']}"

# --- NUEVA PRUEBA: Leer Tipo Vehículo No Encontrado (404) ---
@pytest.mark.asyncio
async def test_leer_tipo_vehiculo_not_found(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba GET /tipos_vehiculo/{id} para un ID que no existe.
    Debería devolver 404 Not Found.
    """
    # 1. Preparación: Obtener token y generar un ID inexistente
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "get_404_tipov")
    non_existent_uuid = uuid.uuid4() # UUID aleatorio

    # 2. Ejecutar la petición GET con el ID inexistente
    response = await client.get(f"/tipos_vehiculo/{non_existent_uuid}", headers=headers)

    # 3. Verificar que la respuesta sea 404 Not Found
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 (Not Found), obtenido {response.status_code}: {response.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response.json()
    assert "detail" in data
    # Asegúrate que este mensaje coincida con el que pusiste en routers/tipos_vehiculo.py
    expected_detail = f"Tipo de vehículo con ID {non_existent_uuid} no encontrado."
    assert data["detail"] == expected_detail

# --- Aquí añadiremos más pruebas (update, etc.) ---
# --- NUEVA PRUEBA: Actualizar Tipo Vehículo Exitosamente ---
@pytest.mark.asyncio
async def test_actualizar_tipo_vehiculo_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba la actualización exitosa de un tipo de vehículo via PUT /tipos_vehiculo/{id}.
    """
    # 1. Preparación: Crear un tipo de vehículo inicial
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "update_tipov")
    nombre_original = f"Tipo Vehículo Original {uuid.uuid4()}"
    tipo_vehiculo_inicial_data = {
        "nombre": nombre_original,
        "ejes_standard": 2,
        "activo": True
    }
    response_create = await client.post("/tipos_vehiculo/", json=tipo_vehiculo_inicial_data, headers=headers)
    assert response_create.status_code == status.HTTP_201_CREATED, "Fallo al crear tipo vehículo inicial para actualizar"
    created_data = response_create.json()
    tipo_vehiculo_id = created_data["id"]
    tipo_vehiculo_id_uuid = uuid.UUID(tipo_vehiculo_id)

    # 2. Definir los datos para la actualización
    nombre_nuevo = f"Tipo Vehículo Actualizado {uuid.uuid4()}"
    descripcion_nueva = "Descripción actualizada para la prueba."
    ejes_nuevos = 4 # Valor válido
    update_payload = {
        "nombre": nombre_nuevo,
        "descripcion": descripcion_nueva,
        "ejes_standard": ejes_nuevos,
        "activo": False # Cambiar estado
    }

    # 3. Ejecutar la petición PUT
    response_update = await client.put(
        f"/tipos_vehiculo/{tipo_vehiculo_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar la Respuesta HTTP
    assert response_update.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 OK para PUT, obtenido {response_update.status_code}: {response_update.text}"
    updated_response_data = response_update.json()

    # Verificar que la respuesta contenga los datos actualizados
    assert updated_response_data["id"] == tipo_vehiculo_id
    assert updated_response_data["nombre"] == nombre_nuevo
    assert updated_response_data["descripcion"] == descripcion_nueva
    assert updated_response_data["ejes_standard"] == ejes_nuevos
    assert updated_response_data["activo"] == update_payload["activo"]
    assert "actualizado_en" in updated_response_data and updated_response_data["actualizado_en"] is not None

    # 5. Verificar directamente en la Base de Datos
    await db_session.refresh(await db_session.get(TipoVehiculo, tipo_vehiculo_id_uuid)) # Recargar objeto
    db_tipo_vehiculo_updated = await db_session.get(TipoVehiculo, tipo_vehiculo_id_uuid) # Obtener el objeto refrescado

    assert db_tipo_vehiculo_updated is not None
    assert db_tipo_vehiculo_updated.nombre == nombre_nuevo
    assert db_tipo_vehiculo_updated.descripcion == descripcion_nueva
    assert db_tipo_vehiculo_updated.ejes_standard == ejes_nuevos
    assert db_tipo_vehiculo_updated.activo == update_payload["activo"]
    assert db_tipo_vehiculo_updated.actualizado_en is not None
    assert db_tipo_vehiculo_updated.actualizado_por == uuid.UUID(user_id)

# --- Aquí añadiremos más pruebas (update 404, update 409) ---

# --- NUEVA PRUEBA: Actualizar Tipo Vehículo No Encontrado (404) ---
@pytest.mark.asyncio
async def test_actualizar_tipo_vehiculo_not_found(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /tipos_vehiculo/{id} para un ID que no existe.
    Debería devolver 404 Not Found.
    """
    # 1. Preparación: Obtener token y generar ID inexistente
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "put_404_tipov")
    non_existent_uuid = uuid.uuid4() # UUID aleatorio

    # Datos de actualización (el contenido no importa mucho)
    update_payload = {
        "nombre": "Tipo Fantasma Actualizado",
        "ejes_standard": 5 # Valor válido
    }

    # 2. Ejecutar la petición PUT con el ID inexistente
    response = await client.put(
        f"/tipos_vehiculo/{non_existent_uuid}",
        json=update_payload,
        headers=headers
    )

    # 3. Verificar que la respuesta sea 404 Not Found
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 (Not Found) para PUT ID inexistente, obtenido {response.status_code}: {response.text}"

    # 4. (Opcional) Verificar el mensaje de detalle del error
    data = response.json()
    assert "detail" in data
    # Asegúrate que este mensaje coincida con el que pusiste en routers/tipos_vehiculo.py
    expected_detail = f"Tipo de vehículo con ID {non_existent_uuid} no encontrado para actualizar."
    assert data["detail"] == expected_detail

# --- Aquí añadiremos más pruebas (update 409) ---
# --- NUEVA PRUEBA: Actualizar Tipo Vehículo con Nombre Duplicado (409) ---
@pytest.mark.asyncio
async def test_actualizar_tipo_vehiculo_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /tipos_vehiculo/{id} intentando asignar un nombre que ya existe en otro tipo.
    Debería devolver 409 Conflict.
    """
    # 1. Preparación: Crear dos tipos de vehículo
    user_id, headers = await create_user_and_get_token_for_tipov_tests(client, db_session, "put_dup_tipov")
    nombre_existente = f"Nombre Existente TV PUT {uuid.uuid4()}"

    # Tipo Vehículo A (cuyo nombre usaremos como duplicado)
    tipo_a_data = {"nombre": nombre_existente, "ejes_standard": 2}
    response_a = await client.post("/tipos_vehiculo/", json=tipo_a_data, headers=headers)
    assert response_a.status_code == status.HTTP_201_CREATED, "Fallo al crear Tipo A"
    tipo_a_id = response_a.json()["id"]

    # Tipo Vehículo B (el que intentaremos actualizar)
    tipo_b_data = {"nombre": f"Nombre Original TV B {uuid.uuid4()}", "ejes_standard": 3}
    response_b = await client.post("/tipos_vehiculo/", json=tipo_b_data, headers=headers)
    assert response_b.status_code == status.HTTP_201_CREATED, "Fallo al crear Tipo B"
    tipo_b_id = response_b.json()["id"]

    # 2. Definir payload para intentar actualizar B con el nombre de A
    update_payload = {
        "nombre": nombre_existente # <-- Intentando usar el nombre de Tipo A
    }

    # 3. Ejecutar la petición PUT sobre Tipo B
    response_update = await client.put(
        f"/tipos_vehiculo/{tipo_b_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar que la respuesta sea 409 Conflict
    assert response_update.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 para PUT con nombre duplicado, obtenido {response_update.status_code}: {response_update.text}"

    # 5. (Opcional) Verificar el mensaje de detalle del error
    data = response_update.json()
    assert "detail" in data
    # Verificar contra los posibles mensajes de error (simple o de IntegrityError)
    expected_detail_simple = f"Ya existe otro tipo de vehículo con el nombre '{nombre_existente}'"
    expected_detail_complex = f"Conflicto al guardar. El nombre '{nombre_existente}' ya podría existir (insensible a mayúsculas/acentos) o hubo otro problema."
    assert data["detail"] == expected_detail_simple or expected_detail_complex in data["detail"], \
           f"Mensaje de error inesperado: {data['detail']}"

# --- Fin de las pruebas para tipos de vehículo ---