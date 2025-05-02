# tests/test_vehiculos.py
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select # Necesario para helpers
from sqlmodel.ext.asyncio.session import AsyncSession
# Importar modelos, schemas y helpers necesarios
from models.usuario import Usuario
from models.tipo_vehiculo import TipoVehiculo # Necesario
from models.vehiculo import Vehiculo # Necesario
from core.security import create_access_token, get_password_hash # Para auth

# --- Funciones Helper (Adaptadas para tests de vehículos) ---
async def create_user_and_get_token_for_veh_tests( # Nombre específico
    client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
    """Crea un usuario único para tests de vehículos y devuelve su ID y headers con token."""
    user_password = f"password_veh_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_veh_{user_suffix}"
    email = f"veh_{user_suffix}@example.com"
    # Verificar si ya existe
    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user = (await db_session.exec(stmt_user)).first()
    if not existing_user:
        user = Usuario(
            username=username, email=email, password_hash=hashed_password, activo=True, rol="OPERADOR"
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

    login_data = {"username": user.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    if response_token.status_code != status.HTTP_200_OK:
         pytest.fail(f"Fallo al obtener token en helper veh_tests para user {user.username}: {response_token.status_code} {response_token.text}")
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return user_id, headers

async def get_or_create_tipo_vehiculo(db_session: AsyncSession, nombre: str = "Camión Test General") -> TipoVehiculo:
    """Obtiene o crea un tipo de vehículo para usar en las pruebas."""
    stmt = select(TipoVehiculo).where(TipoVehiculo.nombre == nombre)
    results = await db_session.exec(stmt)
    tipo = results.first()
    if not tipo:
        tipo = TipoVehiculo(nombre=nombre)
        db_session.add(tipo)
        await db_session.commit()
        await db_session.refresh(tipo)
    return tipo
# --- Fin Funciones Helper ---
# --- Pruebas ---
@pytest.mark.asyncio
async def test_crear_leer_eliminar_vehiculo(client: AsyncClient, db_session: AsyncSession):
    """Prueba el ciclo básico Crear, Leer, Eliminar(Lógico) para un vehículo."""
    # Preparación
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "crud_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)

    # 1. Crear vehículo
    vehiculo_data = {
        "numero_economico": "ECO-CRUD-VEH-01", # Usar prefijos únicos ayuda
        "placa": "CRUD-VEH-001",
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response = await client.post("/vehiculos/", json=vehiculo_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Status Crear Veh: {response.status_code} {response.text}"
    created_data = response.json()
    vehiculo_id = created_data["id"]
    vehiculo_id_uuid = uuid.UUID(vehiculo_id)

    # 2. Leer vehículo creado
    response = await client.get(f"/vehiculos/{vehiculo_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"Status Leer Veh: {response.status_code} {response.text}"
    read_data = response.json()
    assert read_data["numero_economico"] == vehiculo_data["numero_economico"]
    assert read_data["placa"] == vehiculo_data["placa"]

    # 3. Eliminación lógica
    response = await client.delete(f"/vehiculos/{vehiculo_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Status Delete Veh: {response.status_code}"

    # 4. Verificar inactivo en BD
    # Refrescar para obtener el estado actualizado después del DELETE
    # Es posible que el objeto de la sesión aún tenga activo=True si no se refresca.
    # Una alternativa es volver a obtenerlo con session.get()
    db_vehiculo = await db_session.get(Vehiculo, vehiculo_id_uuid)
    # await db_session.refresh(db_vehiculo) # O refrescar si ya lo tenías
    assert db_vehiculo is not None
    assert not db_vehiculo.activo
    assert db_vehiculo.fecha_baja is not None

# --- NUEVA PRUEBA: Leer Vehículo No Encontrado ---
@pytest.mark.asyncio
async def test_leer_vehiculo_not_found(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /vehiculos/{id} para un ID que no existe."""
    # Preparación: Solo necesitamos un token válido
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "get_404_veh")
    non_existent_id = uuid.uuid4()

    # Ejecución
    response = await client.get(f"/vehiculos/{non_existent_id}", headers=headers)

    # Verificación
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404, obtenido {response.status_code}: {response.text}"
    data = response.json()
    assert "detail" in data
    assert f"Vehículo con ID {non_existent_id} no encontrado" in data["detail"] # Asegúrate que este mensaje coincida

# --- NUEVA PRUEBA: Crear Vehículo con Número Económico Duplicado ---
@pytest.mark.asyncio
async def test_crear_vehiculo_duplicado_num_eco(client: AsyncClient, db_session: AsyncSession):
    """Prueba POST /vehiculos/ con un numero_economico duplicado."""
    # Preparación
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "eco_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    num_eco_duplicado = "ECO-DUP-VEH-789" # Usar un número diferente a otras pruebas

    # 1. Crear el primer vehículo
    vehiculo_1_data = {
        "numero_economico": num_eco_duplicado,
        "placa": "DUP-ECO-VEH-1", # Placa única
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response1 = await client.post("/vehiculos/", json=vehiculo_1_data, headers=headers)
    assert response1.status_code == status.HTTP_201_CREATED, f"Fallo al crear vehículo inicial: {response1.text}"

    # 2. Intentar crear un segundo vehículo con el MISMO numero_economico
    vehiculo_2_data = {
        "numero_economico": num_eco_duplicado, # <-- Duplicado
        "placa": "DUP-ECO-VEH-2", # Placa diferente y única
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response2 = await client.post("/vehiculos/", json=vehiculo_2_data, headers=headers)

    # 3. Verificar respuesta 409 Conflict
    assert response2.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 num_eco, obtenido {response2.status_code}: {response2.text}"
    data = response2.json()
    assert "detail" in data
    assert f"Ya existe vehículo con número económico '{num_eco_duplicado}'" in data["detail"] # Asegúrate que este mensaje coincida

# --- NUEVA PRUEBA: Crear Vehículo con Placa Duplicada ---
@pytest.mark.asyncio
async def test_crear_vehiculo_duplicado_placa(client: AsyncClient, db_session: AsyncSession):
    """Prueba POST /vehiculos/ con una placa duplicada."""
    # Preparación
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "placa_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    placa_duplicada = "DUP-PLA-789" # Placa que vamos a duplicar

    # 1. Crear el primer vehículo
    vehiculo_1_data = {
        "numero_economico": "ECO-PLA-DUP-1", # Num Eco único
        "placa": placa_duplicada,            # La placa que se duplicará
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response1 = await client.post("/vehiculos/", json=vehiculo_1_data, headers=headers)
    assert response1.status_code == status.HTTP_201_CREATED, f"Fallo al crear vehículo inicial (placa dup test): {response1.text}"

    # 2. Intentar crear un segundo vehículo con la MISMA placa
    vehiculo_2_data = {
        "numero_economico": "ECO-PLA-DUP-2", # Num Eco diferente y único
        "placa": placa_duplicada,            # <-- Placa Duplicada
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response2 = await client.post("/vehiculos/", json=vehiculo_2_data, headers=headers)

    # 3. Verificar respuesta 409 Conflict
    assert response2.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 (placa dup), obtenido {response2.status_code}: {response2.text}"
    data = response2.json()
    assert "detail" in data
    # Ajusta el mensaje si es diferente en tu router vehiculos.py
    assert f"Ya existe vehículo con placa '{placa_duplicada}'" in data["detail"]

# --- NUEVA PRUEBA: Actualizar Vehículo (Éxito) ---
@pytest.mark.asyncio
async def test_actualizar_vehiculo_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba la actualización exitosa de un vehículo via PUT /vehiculos/{id}."""
    # Preparación
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "update_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)

    # 1. Crear el vehículo que vamos a actualizar
    vehiculo_initial_data = {
        "numero_economico": "ECO-TO-UPDATE-1",
        "placa": "UPD-ME-1",
        "tipo_vehiculo_id": str(tipo_vehiculo.id),
        "marca": "Marca Original",
        "modelo_vehiculo": "Modelo Original",
        "activo": True
    }
    response_create = await client.post("/vehiculos/", json=vehiculo_initial_data, headers=headers)
    assert response_create.status_code == status.HTTP_201_CREATED, f"Fallo al crear vehículo para actualizar: {response_create.text}"
    created_data = response_create.json()
    vehiculo_id = created_data["id"]
    vehiculo_id_uuid = uuid.UUID(vehiculo_id)

    # 2. Definir los datos para la actualización
    update_payload = {
        "placa": "UPDATED-1", # Cambiamos la placa
        "marca": "Marca Actualizada", # Cambiamos la marca
        "activo": False, # Cambiamos el estado
        "notas": "Vehículo actualizado en prueba." # Añadimos notas
        # No actualizamos numero_economico ni tipo_vehiculo_id en esta prueba
    }

    # 3. Llamar al endpoint PUT /vehiculos/{vehiculo_id}
    response_update = await client.put(
        f"/vehiculos/{vehiculo_id}",
        json=update_payload,
        headers=headers
    )

    # 4. Verificar la respuesta HTTP
    assert response_update.status_code == status.HTTP_200_OK, \
        f"Status esperado 200 para PUT, obtenido {response_update.status_code}: {response_update.text}"
    updated_response_data = response_update.json()

    # Verificar que la respuesta contenga los datos actualizados
    assert updated_response_data["id"] == vehiculo_id
    assert updated_response_data["numero_economico"] == vehiculo_initial_data["numero_economico"] # No cambió
    assert updated_response_data["placa"] == update_payload["placa"] # ¡Cambió!
    assert updated_response_data["marca"] == update_payload["marca"] # ¡Cambió!
    assert updated_response_data["activo"] == update_payload["activo"] # ¡Cambió!
    assert updated_response_data["notas"] == update_payload["notas"] # ¡Se añadió!
    assert updated_response_data["actualizado_en"] is not None # Se actualizó la fecha

    # 5. Verificar directamente en la Base de Datos
    db_vehiculo_updated = await db_session.get(Vehiculo, vehiculo_id_uuid)
    assert db_vehiculo_updated is not None
    assert db_vehiculo_updated.placa == update_payload["placa"]
    assert db_vehiculo_updated.marca == update_payload["marca"]
    assert db_vehiculo_updated.activo == update_payload["activo"]
    assert db_vehiculo_updated.notas == update_payload["notas"]
    assert db_vehiculo_updated.actualizado_en is not None
    # assert db_vehiculo_updated.actualizado_por == uuid.UUID(user_id) # Verificar quién actualizó

# --- NUEVA PRUEBA: Actualizar Vehículo No Encontrado (404) ---
@pytest.mark.asyncio
async def test_actualizar_vehiculo_not_found(client: AsyncClient, db_session: AsyncSession):
    """Prueba PUT /vehiculos/{id} para un ID que no existe."""
    # Preparación: Solo necesitamos un token válido y un ID inexistente
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "put_404_veh")
    non_existent_id = uuid.uuid4()

    # Datos de actualización (no importa el contenido, la petición fallará antes)
    update_payload = {
        "marca": "Marca Fantasma",
        "notas": "Intentando actualizar algo que no existe"
    }

    # Ejecución: Intentar actualizar el ID inexistente
    response = await client.put(
        f"/vehiculos/{non_existent_id}",
        json=update_payload,
        headers=headers
    )

    # Verificación
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Status esperado 404 para PUT ID inexistente, obtenido {response.status_code}: {response.text}"
    data = response.json()
    assert "detail" in data
    # Ajusta el mensaje si es diferente en tu router/vehiculos.py
    assert f"Vehículo con ID {non_existent_id} no encontrado para actualizar" in data["detail"]

# --- Aquí añadiremos las pruebas para PUT 409 después ---
# --- NUEVA PRUEBA: Actualizar Vehículo con Num Eco Duplicado (409) ---
@pytest.mark.asyncio
async def test_actualizar_vehiculo_duplicado_num_eco(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /vehiculos/{id} intentando asignar un numero_economico que ya existe en otro vehículo.
    """
    # Preparación
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "put_eco_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)

    # 1. Crear el vehículo A (cuyo numero_economico NO cambiaremos)
    num_eco_existente = "ECO-EXIST-PUT-1"
    vehiculo_a_data = {
        "numero_economico": num_eco_existente,
        "placa": "PLAC-PUT-A",
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response_a = await client.post("/vehiculos/", json=vehiculo_a_data, headers=headers)
    assert response_a.status_code == status.HTTP_201_CREATED, f"Fallo al crear vehículo A: {response_a.text}"

    # 2. Crear el vehículo B (el que intentaremos actualizar)
    vehiculo_b_data = {
        "numero_economico": "ECO-TO-CHANGE-B",
        "placa": "PLAC-PUT-B",
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response_b = await client.post("/vehiculos/", json=vehiculo_b_data, headers=headers)
    assert response_b.status_code == status.HTTP_201_CREATED, f"Fallo al crear vehículo B: {response_b.text}"
    vehiculo_b_id = response_b.json()["id"]

    # 3. Intentar actualizar Vehículo B para usar el numero_economico del Vehículo A
    update_payload = {
        "numero_economico": num_eco_existente # <-- Intentando usar el num_eco de Vehículo A
    }

    # Ejecución
    response_update = await client.put(
        f"/vehiculos/{vehiculo_b_id}",
        json=update_payload,
        headers=headers
    )

    # Verificación
    assert response_update.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 para PUT num_eco dup, obtenido {response_update.status_code}: {response_update.text}"
    data = response_update.json()
    assert "detail" in data
    # Ajusta el mensaje si es diferente en tu router/vehiculos.py
    assert f"Número económico '{num_eco_existente}' ya existe" in data["detail"]

# --- NUEVA PRUEBA: Actualizar Vehículo con Placa Duplicada (409) ---
@pytest.mark.asyncio
async def test_actualizar_vehiculo_duplicado_placa(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba PUT /vehiculos/{id} intentando asignar una placa que ya existe en otro vehículo.
    """
    # Preparación
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "put_placa_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)

    # 1. Crear el vehículo A (cuya placa NO cambiaremos)
    placa_existente = "DUP-PLACA-PUT-1"
    vehiculo_a_data = {
        "numero_economico": "ECO-PUT-PLACA-A",
        "placa": placa_existente,
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response_a = await client.post("/vehiculos/", json=vehiculo_a_data, headers=headers)
    assert response_a.status_code == status.HTTP_201_CREATED, f"Fallo al crear vehículo A (placa dup): {response_a.text}"

    # 2. Crear el vehículo B (el que intentaremos actualizar)
    vehiculo_b_data = {
        "numero_economico": "ECO-PUT-PLACA-B",
        "placa": "PLAC-PUT-B-ORIG", # Placa original única
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response_b = await client.post("/vehiculos/", json=vehiculo_b_data, headers=headers)
    assert response_b.status_code == status.HTTP_201_CREATED, f"Fallo al crear vehículo B (placa dup): {response_b.text}"
    vehiculo_b_id = response_b.json()["id"]

    # 3. Intentar actualizar Vehículo B para usar la placa del Vehículo A
    update_payload = {
        "placa": placa_existente # <-- Intentando usar la placa de Vehículo A
    }

    # Ejecución
    response_update = await client.put(
        f"/vehiculos/{vehiculo_b_id}",
        json=update_payload,
        headers=headers
    )

    # Verificación
    assert response_update.status_code == status.HTTP_409_CONFLICT, \
        f"Status esperado 409 para PUT placa dup, obtenido {response_update.status_code}: {response_update.text}"
    data = response_update.json()
    assert "detail" in data
    # Ajusta el mensaje si es diferente en tu router/vehiculos.py
    assert f"Placa '{placa_existente}' ya existe" in data["detail"]

# --- Fin pruebas básicas vehículo ---
# --- NUEVA PRUEBA: Listar Vehículos con Filtro Activo ---
@pytest.mark.asyncio
async def test_listar_vehiculos_con_filtro_activo(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba GET /vehiculos/ con el filtro ?activo=true y ?activo=false.
    Verifica que se listen los vehículos correctos según su estado.
    """
    # --- SETUP ---
    # 1. Obtener token y tipo de vehículo
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "list_filter")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session, nombre="Tipo Vehiculo para Filtro")

    # 2. Crear vehículo que permanecerá activo
    vehiculo_activo_data = {
        "numero_economico": f"ECO-ACTIVO-{uuid.uuid4()}",
        "placa": f"ACT-{uuid.uuid4().hex[:6].upper()}",
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response_activo = await client.post("/vehiculos/", json=vehiculo_activo_data, headers=headers)
    assert response_activo.status_code == status.HTTP_201_CREATED, "Fallo al crear vehículo activo"
    vehiculo_activo_id = response_activo.json()["id"]

    # 3. Crear vehículo que se marcará como inactivo
    vehiculo_inactivo_data = {
        "numero_economico": f"ECO-INACTIVO-{uuid.uuid4()}",
        "placa": f"INA-{uuid.uuid4().hex[:6].upper()}",
        "tipo_vehiculo_id": str(tipo_vehiculo.id)
    }
    response_inactivo = await client.post("/vehiculos/", json=vehiculo_inactivo_data, headers=headers)
    assert response_inactivo.status_code == status.HTTP_201_CREATED, "Fallo al crear vehículo para inactivar"
    vehiculo_inactivo_id = response_inactivo.json()["id"]

    # Marcar el segundo vehículo como inactivo usando el endpoint DELETE
    response_delete = await client.delete(f"/vehiculos/{vehiculo_inactivo_id}", headers=headers)
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT, "Fallo al inactivar vehículo"

    # --- EJECUCIÓN Y VERIFICACIÓN (ACTIVOS) ---
    print(f"Buscando activos: GET /vehiculos/?activo=true")
    response_get_activos = await client.get("/vehiculos/", params={"activo": True}, headers=headers)
    assert response_get_activos.status_code == status.HTTP_200_OK, f"Error al obtener activos: {response_get_activos.text}"

    lista_activos = response_get_activos.json()
    ids_activos_encontrados = {v["id"] for v in lista_activos}
    print(f"IDs Activos encontrados: {ids_activos_encontrados}")

    assert vehiculo_activo_id in ids_activos_encontrados, f"Vehículo activo {vehiculo_activo_id} no encontrado en lista de activos"
    assert vehiculo_inactivo_id not in ids_activos_encontrados, f"Vehículo inactivo {vehiculo_inactivo_id} encontrado erróneamente en lista de activos"

    # --- EJECUCIÓN Y VERIFICACIÓN (INACTIVOS) ---
    print(f"Buscando inactivos: GET /vehiculos/?activo=false")
    response_get_inactivos = await client.get("/vehiculos/", params={"activo": False}, headers=headers)
    assert response_get_inactivos.status_code == status.HTTP_200_OK, f"Error al obtener inactivos: {response_get_inactivos.text}"

    lista_inactivos = response_get_inactivos.json()
    ids_inactivos_encontrados = {v["id"] for v in lista_inactivos}
    print(f"IDs Inactivos encontrados: {ids_inactivos_encontrados}")

    assert vehiculo_activo_id not in ids_inactivos_encontrados, f"Vehículo activo {vehiculo_activo_id} encontrado erróneamente en lista de inactivos"
    assert vehiculo_inactivo_id in ids_inactivos_encontrados, f"Vehículo inactivo {vehiculo_inactivo_id} no encontrado en lista de inactivos"

    # --- EJECUCIÓN Y VERIFICACIÓN (TODOS - Opcional) ---
    # print(f"Buscando todos: GET /vehiculos/")
    # response_get_todos = await client.get("/vehiculos/", headers=headers)
    # assert response_get_todos.status_code == status.HTTP_200_OK
    # lista_todos = response_get_todos.json()
    # ids_todos_encontrados = {v["id"] for v in lista_todos}
    # assert vehiculo_activo_id in ids_todos_encontrados
    # assert vehiculo_inactivo_id in ids_todos_encontrados


# --- Fin de la prueba añadida ---
