# tests/test_vehiculos.py (Versión Corregida v3)

import pytest
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Tuple, Dict, Optional
from datetime import datetime, timezone # Importar datetime

# Importar modelos, schemas y helpers necesarios
from models.usuario import Usuario
from models.tipo_vehiculo import TipoVehiculo
from models.vehiculo import Vehiculo
from core.security import create_access_token, get_password_hash, verify_password # verify_password sí se usa aquí

# --- Importar settings y definir prefijos ---
from core.config import settings
API_PREFIX = settings.API_V1_STR
AUTH_PREFIX = f"{API_PREFIX}/auth"
VEHICULOS_PREFIX = f"{API_PREFIX}/vehiculos" # <-- Prefijo para este router

# --- Funciones Helper (CORREGIDO TOKEN URL) ---
async def create_user_and_get_token_for_veh_tests(
    client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
    """Crea un usuario único (OPERADOR) y devuelve ID y headers."""
    user_password = f"password_veh_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_veh_{user_suffix}_{uuid.uuid4().hex[:4]}" # Unicidad
    email = f"veh_{user_suffix}@example.com"
    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user = (await db_session.exec(stmt_user)).first()
    user: Usuario; user_id: Optional[str] = None
    if not existing_user:
        user = Usuario(username=username, email=email, password_hash=hashed_password, activo=True, rol="OPERADOR", creado_en=datetime.now(timezone.utc))
        db_session.add(user); await db_session.commit(); await db_session.refresh(user)
        user_id = str(user.id)
    else:
        if not verify_password(user_password, existing_user.password_hash or ""): existing_user.password_hash = hashed_password
        existing_user.activo=True; existing_user.rol="OPERADOR"; existing_user.actualizado_en=datetime.now(timezone.utc)
        db_session.add(existing_user); await db_session.commit(); await db_session.refresh(existing_user)
        user_id = str(existing_user.id); user = existing_user
    if user_id is None: pytest.fail(f"No se pudo obtener/crear user_id para {username}")

    login_data = {"username": user.username, "password": user_password}
    # ==========================
    # ===== RUTA TOKEN OK! =====
    token_url = f"{AUTH_PREFIX}/token" # Usar el prefijo de Auth
    # ==========================
    response_token = await client.post(token_url, data=login_data)
    if response_token.status_code != status.HTTP_200_OK: pytest.fail(f"Fallo al obtener token: {response_token.status_code} {response_token.text}")
    token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, headers

async def get_or_create_tipo_vehiculo(db_session: AsyncSession, nombre: str = "Camión Test General") -> TipoVehiculo:
    """Obtiene o crea un tipo de vehículo."""
    stmt = select(TipoVehiculo).where(TipoVehiculo.nombre == nombre)
    tipo = (await db_session.exec(stmt)).first()
    if not tipo:
        user_result = await db_session.exec(select(Usuario).limit(1)) # Necesita user_id si es obligatorio
        user = user_result.first()
        creador_id = user.id if user else None
        tipo = TipoVehiculo(nombre=nombre, ejes_standard=3, creado_por=creador_id)
        db_session.add(tipo); await db_session.commit(); await db_session.refresh(tipo)
    return tipo
# --- Fin Funciones Helper ---

# --- Pruebas (URLs Corregidas con VEHICULOS_PREFIX) ---
@pytest.mark.asyncio
async def test_crear_leer_eliminar_vehiculo(client: AsyncClient, db_session: AsyncSession):
    """Prueba el ciclo básico Crear, Leer, Eliminar(Lógico) para un vehículo."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "crud_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    vehiculo_data = {"numero_economico": f"ECO-CRUD-{uuid.uuid4().hex[:4]}", "placa": f"CRU-{uuid.uuid4().hex[:6]}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    url_base = f"{VEHICULOS_PREFIX}/" # <-- URL Corregida
    response = await client.post(url_base, json=vehiculo_data, headers=headers); assert response.status_code == status.HTTP_201_CREATED
    vehiculo_id = response.json()["id"]; vehiculo_id_uuid = uuid.UUID(vehiculo_id)
    url_detalle = f"{VEHICULOS_PREFIX}/{vehiculo_id}" # <-- URL Corregida
    response_get = await client.get(url_detalle, headers=headers); assert response_get.status_code == status.HTTP_200_OK
    response_delete = await client.delete(url_detalle, headers=headers); assert response_delete.status_code == status.HTTP_204_NO_CONTENT
    db_vehiculo = await db_session.get(Vehiculo, vehiculo_id_uuid); assert db_vehiculo and not db_vehiculo.activo

@pytest.mark.asyncio
async def test_leer_vehiculo_not_found(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /vehiculos/{id} inexistente -> 404."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "get_404_veh")
    non_existent_id = uuid.uuid4()
    url_get = f"{VEHICULOS_PREFIX}/{non_existent_id}" # <-- URL Corregida
    response = await client.get(url_get, headers=headers); assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_crear_vehiculo_duplicado_num_eco(client: AsyncClient, db_session: AsyncSession):
    """Prueba POST /vehiculos/ con num_eco duplicado -> 409."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "eco_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    num_eco_duplicado = f"ECO-DUP-{uuid.uuid4().hex[:6]}"
    url_base = f"{VEHICULOS_PREFIX}/" # <-- URL Corregida
    vehiculo_1_data = {"numero_economico": num_eco_duplicado, "placa": f"DUP1-{uuid.uuid4().hex[:6]}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    resp1 = await client.post(url_base, json=vehiculo_1_data, headers=headers); assert resp1.status_code == status.HTTP_201_CREATED
    vehiculo_2_data = {"numero_economico": num_eco_duplicado, "placa": f"DUP2-{uuid.uuid4().hex[:6]}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    resp2 = await client.post(url_base, json=vehiculo_2_data, headers=headers); assert resp2.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_crear_vehiculo_duplicado_placa(client: AsyncClient, db_session: AsyncSession):
    """Prueba POST /vehiculos/ con placa duplicada -> 409."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "placa_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    placa_duplicada = f"DUP-PLA-{uuid.uuid4().hex[:6].upper()}"
    url_base = f"{VEHICULOS_PREFIX}/" # <-- URL Corregida
    vehiculo_1_data = {"numero_economico": f"ECO1-{uuid.uuid4().hex[:6]}", "placa": placa_duplicada, "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    resp1 = await client.post(url_base, json=vehiculo_1_data, headers=headers); assert resp1.status_code == status.HTTP_201_CREATED
    vehiculo_2_data = {"numero_economico": f"ECO2-{uuid.uuid4().hex[:6]}", "placa": placa_duplicada, "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    resp2 = await client.post(url_base, json=vehiculo_2_data, headers=headers); assert resp2.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_actualizar_vehiculo_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba actualización exitosa PUT /vehiculos/{id}."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "update_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    url_base = f"{VEHICULOS_PREFIX}/" # <-- URL Corregida
    vehiculo_initial_data = {"numero_economico": f"ECO-UPD-{uuid.uuid4().hex[:6]}", "placa": f"UPD-{uuid.uuid4().hex[:6]}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    resp_create = await client.post(url_base, json=vehiculo_initial_data, headers=headers); assert resp_create.status_code == status.HTTP_201_CREATED
    vehiculo_id = resp_create.json()["id"]
    url_put = f"{VEHICULOS_PREFIX}/{vehiculo_id}" # <-- URL Corregida
    update_payload = {"placa": f"UPDATED-{uuid.uuid4().hex[:6]}", "marca": "Marca Actualizada", "activo": False}
    response_update = await client.put(url_put, json=update_payload, headers=headers); assert response_update.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_actualizar_vehiculo_not_found(client: AsyncClient, db_session: AsyncSession):
    """Prueba PUT /vehiculos/{id} inexistente -> 404."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "put_404_veh")
    non_existent_id = uuid.uuid4()
    url_put = f"{VEHICULOS_PREFIX}/{non_existent_id}" # <-- URL Corregida
    response = await client.put(url_put, json={"marca": "Fantasma"}, headers=headers); assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_actualizar_vehiculo_duplicado_num_eco(client: AsyncClient, db_session: AsyncSession):
    """Prueba PUT /vehiculos/{id} con num_eco duplicado -> 409."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "put_eco_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    num_eco_existente = f"ECO-EXIST-{uuid.uuid4().hex[:6]}"
    url_base = f"{VEHICULOS_PREFIX}/" # <-- URL Corregida
    resp_a = await client.post(url_base, json={"numero_economico": num_eco_existente, "placa": f"PLAC-A-{uuid.uuid4().hex[:6]}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}, headers=headers); assert resp_a.status_code == status.HTTP_201_CREATED
    resp_b = await client.post(url_base, json={"numero_economico": f"ECO-B-{uuid.uuid4().hex[:6]}", "placa": f"PLAC-B-{uuid.uuid4().hex[:6]}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}, headers=headers); assert resp_b.status_code == status.HTTP_201_CREATED
    vehiculo_b_id = resp_b.json()["id"]
    url_put = f"{VEHICULOS_PREFIX}/{vehiculo_b_id}" # <-- URL Corregida
    response_update = await client.put(url_put, json={"numero_economico": num_eco_existente}, headers=headers); assert response_update.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_actualizar_vehiculo_duplicado_placa(client: AsyncClient, db_session: AsyncSession):
    """Prueba PUT /vehiculos/{id} con placa duplicada -> 409."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "put_placa_dup_veh")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session)
    placa_existente = f"DUP-PLA-{uuid.uuid4().hex[:6].upper()}"
    url_base = f"{VEHICULOS_PREFIX}/" # <-- URL Corregida
    resp_a = await client.post(url_base, json={"numero_economico": f"ECO-A-{uuid.uuid4().hex[:6]}", "placa": placa_existente, "tipo_vehiculo_id": str(tipo_vehiculo.id)}, headers=headers); assert resp_a.status_code == status.HTTP_201_CREATED
    resp_b = await client.post(url_base, json={"numero_economico": f"ECO-B-{uuid.uuid4().hex[:6]}", "placa": f"PLAC-B-{uuid.uuid4().hex[:6]}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}, headers=headers); assert resp_b.status_code == status.HTTP_201_CREATED
    vehiculo_b_id = resp_b.json()["id"]
    url_put = f"{VEHICULOS_PREFIX}/{vehiculo_b_id}" # <-- URL Corregida
    response_update = await client.put(url_put, json={"placa": placa_existente}, headers=headers); assert response_update.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_listar_vehiculos_con_filtro_activo(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /vehiculos/ con filtro ?activo=true y ?activo=false."""
    user_id, headers = await create_user_and_get_token_for_veh_tests(client, db_session, "list_filter")
    tipo_vehiculo = await get_or_create_tipo_vehiculo(db_session, nombre="Tipo Vehiculo para Filtro")
    url_base = f"{VEHICULOS_PREFIX}/" # <-- URL Corregida

    vehiculo_activo_data = {"numero_economico": f"ECO-ACT-{uuid.uuid4()}", "placa": f"ACT-{uuid.uuid4().hex[:6].upper()}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    resp_activo = await client.post(url_base, json=vehiculo_activo_data, headers=headers); assert resp_activo.status_code == status.HTTP_201_CREATED
    vehiculo_activo_id = resp_activo.json()["id"]

    vehiculo_inactivo_data = {"numero_economico": f"ECO-INACT-{uuid.uuid4()}", "placa": f"INA-{uuid.uuid4().hex[:6].upper()}", "tipo_vehiculo_id": str(tipo_vehiculo.id)}
    resp_inactivo = await client.post(url_base, json=vehiculo_inactivo_data, headers=headers); assert resp_inactivo.status_code == status.HTTP_201_CREATED
    vehiculo_inactivo_id = resp_inactivo.json()["id"]

    url_delete = f"{VEHICULOS_PREFIX}/{vehiculo_inactivo_id}" # <-- URL Corregida
    resp_delete = await client.delete(url_delete, headers=headers); assert resp_delete.status_code == status.HTTP_204_NO_CONTENT

    response_get_activos = await client.get(url_base, params={"activo": True}, headers=headers); assert response_get_activos.status_code == status.HTTP_200_OK # <-- URL Corregida
    ids_activos = {v["id"] for v in response_get_activos.json()}
    assert vehiculo_activo_id in ids_activos; assert vehiculo_inactivo_id not in ids_activos

    response_get_inactivos = await client.get(url_base, params={"activo": False}, headers=headers); assert response_get_inactivos.status_code == status.HTTP_200_OK # <-- URL Corregida
    ids_inactivos = {v["id"] for v in response_get_inactivos.json()}
    assert vehiculo_activo_id not in ids_inactivos; assert vehiculo_inactivo_id in ids_inactivos

# ===== FIN DE tests/test_vehiculos.py =====