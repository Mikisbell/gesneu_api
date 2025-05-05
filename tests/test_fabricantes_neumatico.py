# tests/test_fabricantes_neumatico.py (Versión Corregida v2)

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
from models.fabricante import FabricanteNeumatico
from schemas.fabricante import FabricanteNeumaticoRead, FabricanteNeumaticoUpdate
from core.security import get_password_hash, verify_password

# --- Importar settings y definir prefijos ---
from core.config import settings
API_PREFIX = settings.API_V1_STR
AUTH_PREFIX = f"{API_PREFIX}/auth"
# --- CORRECCIÓN PREFIJO ROUTER ---
FABRICANTES_PREFIX = f"{API_PREFIX}/fabricantes-neumatico" # <-- Debe coincidir con main.py

# --- Helper Corregido ---
async def create_user_and_get_token_for_fabr_tests(
    client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
    """Crea un usuario único (ADMIN) y devuelve ID y headers (CORREGIDO)."""
    user_password = f"password_fabr_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_fabr_{user_suffix}_{uuid.uuid4().hex[:4]}"
    email = f"fabr_{user_suffix}@example.com"
    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user = (await db_session.exec(stmt_user)).first()
    user: Usuario; user_id: Optional[str] = None
    if not existing_user:
        user = Usuario(username=username, email=email, password_hash=hashed_password, activo=True, rol="ADMIN", creado_en=datetime.now(timezone.utc))
        db_session.add(user); await db_session.commit(); await db_session.refresh(user)
        user_id = str(user.id)
    else:
        if not verify_password(user_password, existing_user.password_hash or ""): existing_user.password_hash = hashed_password
        existing_user.activo=True; existing_user.rol="ADMIN"; existing_user.actualizado_en=datetime.now(timezone.utc)
        db_session.add(existing_user); await db_session.commit(); await db_session.refresh(existing_user)
        user_id = str(existing_user.id); user = existing_user
    if user_id is None: pytest.fail(f"No se pudo obtener/crear user_id para {username}")

    login_data = {"username": user.username, "password": user_password}

    # --- LA CORRECCIÓN ESTÁ AQUÍ ---
    token_url = f"{AUTH_PREFIX}/token" # Usar el prefijo de Auth definido arriba
    response_token = await client.post(token_url, data=login_data) # Llamar a la URL correcta
    # --- FIN DE LA CORRECCIÓN ---

    if response_token.status_code != status.HTTP_200_OK: pytest.fail(f"Fallo al obtener token: {response_token.status_code} {response_token.text}")
    token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, headers
# --- Fin Helper ---

# --- Tu función de prueba (test_crear_leer_desactivar_fabricante) va aquí ---
# (El código que pegaste para esta función ya estaba bien respecto a los prefijos de endpoints)
@pytest.mark.asyncio
async def test_crear_leer_desactivar_fabricante(client: AsyncClient, db_session: AsyncSession):
    # Esta función llama al helper corregido de arriba
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "crud_fabr")
    user_uuid = uuid.UUID(user_id)
    fabricante_data = {"nombre": f"Fab CRUD {uuid.uuid4()}", "codigo_abreviado": f"FAB-{uuid.uuid4().hex[:6]}"}
    url_base = f"{FABRICANTES_PREFIX}/" # <-- Ya usa el prefijo correcto
    response = await client.post(url_base, json=fabricante_data, headers=headers); assert response.status_code == status.HTTP_201_CREATED
    fabricante_id = response.json()["id"]; fabricante_id_uuid = uuid.UUID(fabricante_id)
    url_detalle = f"{FABRICANTES_PREFIX}/{fabricante_id}" # <-- Ya usa el prefijo correcto
    response_get = await client.get(url_detalle, headers=headers); assert response_get.status_code == status.HTTP_200_OK
    # Asumiendo que la URL de delete también usa el prefijo
    url_delete = f"{FABRICANTES_PREFIX}/{fabricante_id}"
    response_delete = await client.delete(url_detalle, headers=headers); assert response_delete.status_code == status.HTTP_204_NO_CONTENT
    # El commit aquí podría ser innecesario si la sesión se maneja correctamente por fixtures
    # await db_session.commit()
    db_fab = await db_session.get(FabricanteNeumatico, fabricante_id_uuid); assert db_fab and not db_fab.activo

# ... (resto de funciones de prueba en test_fabricantes_neumatico.py) ...

@pytest.mark.asyncio
async def test_crear_fabricante_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "dup_nom_fabr")
    nombre_duplicado = f"Fab Nombre Dup {uuid.uuid4()}"
    url_base = f"{FABRICANTES_PREFIX}/" # <-- URL Corregida
    resp1 = await client.post(url_base, json={"nombre": nombre_duplicado, "codigo_abreviado": f"FND1-{uuid.uuid4().hex[:5]}"}, headers=headers); assert resp1.status_code == status.HTTP_201_CREATED
    resp2 = await client.post(url_base, json={"nombre": nombre_duplicado, "codigo_abreviado": f"FND2-{uuid.uuid4().hex[:5]}"}, headers=headers); assert resp2.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_crear_fabricante_duplicado_codigo(client: AsyncClient, db_session: AsyncSession):
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "dup_cod_fabr")
    codigo_duplicado = f"FCD-{uuid.uuid4().hex[:6]}"
    url_base = f"{FABRICANTES_PREFIX}/" # <-- URL Corregida
    resp1 = await client.post(url_base, json={"nombre": f"Fab Cod Dup 1 {uuid.uuid4()}", "codigo_abreviado": codigo_duplicado}, headers=headers); assert resp1.status_code == status.HTTP_201_CREATED
    resp2 = await client.post(url_base, json={"nombre": f"Fab Cod Dup 2 {uuid.uuid4()}", "codigo_abreviado": codigo_duplicado}, headers=headers); assert resp2.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_leer_fabricante_not_found(client: AsyncClient, db_session: AsyncSession):
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "get_404_fabr")
    non_existent_uuid = uuid.uuid4()
    url_get = f"{FABRICANTES_PREFIX}/{non_existent_uuid}" # <-- URL Corregida
    response = await client.get(url_get, headers=headers); assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_actualizar_fabricante_success(client: AsyncClient, db_session: AsyncSession):
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "update_fabr")
    url_base = f"{FABRICANTES_PREFIX}/" # <-- URL Corregida
    fab_inicial_data = {"nombre": f"Fab Orig PUT {uuid.uuid4()}", "codigo_abreviado": f"ORI-{uuid.uuid4().hex[:6]}"}
    resp_create = await client.post(url_base, json=fab_inicial_data, headers=headers); assert resp_create.status_code == status.HTTP_201_CREATED
    fab_id = resp_create.json()["id"]
    url_put = f"{FABRICANTES_PREFIX}/{fab_id}" # <-- URL Corregida
    update_payload = {"nombre": f"Fab Upd PUT {uuid.uuid4()}", "codigo_abreviado": f"UPD-{uuid.uuid4().hex[:6]}", "activo": False}
    response_update = await client.put(url_put, json=update_payload, headers=headers); assert response_update.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_actualizar_fabricante_not_found(client: AsyncClient, db_session: AsyncSession):
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "put_404_fabr")
    non_existent_uuid = uuid.uuid4()
    url_put = f"{FABRICANTES_PREFIX}/{non_existent_uuid}" # <-- URL Corregida
    response = await client.put(url_put, json={"nombre": "Fantasma"}, headers=headers); assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_actualizar_fabricante_duplicado_nombre(client: AsyncClient, db_session: AsyncSession):
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "put_dup_nom_fabr")
    nombre_existente = f"Fab Nombre Exist PUT {uuid.uuid4()}"
    url_base = f"{FABRICANTES_PREFIX}/" # <-- URL Corregida
    resp_a = await client.post(url_base, json={"nombre": nombre_existente, "codigo_abreviado": f"PUTA-{uuid.uuid4().hex[:5]}"}, headers=headers); assert resp_a.status_code == status.HTTP_201_CREATED
    resp_b = await client.post(url_base, json={"nombre": f"Fab Orig B {uuid.uuid4()}", "codigo_abreviado": f"PUTB-{uuid.uuid4().hex[:5]}"}, headers=headers); assert resp_b.status_code == status.HTTP_201_CREATED
    fab_b_id = resp_b.json()["id"]
    url_put = f"{FABRICANTES_PREFIX}/{fab_b_id}" # <-- URL Corregida
    response_update = await client.put(url_put, json={"nombre": nombre_existente}, headers=headers); assert response_update.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_actualizar_fabricante_duplicado_codigo(client: AsyncClient, db_session: AsyncSession):
    user_id, headers = await create_user_and_get_token_for_fabr_tests(client, db_session, "put_dup_cod_fabr")
    codigo_existente = f"CODEX-{uuid.uuid4().hex[:4].upper()}"
    url_base = f"{FABRICANTES_PREFIX}/" # <-- URL Corregida
    resp_a = await client.post(url_base, json={"nombre": f"Fab Nom A {uuid.uuid4()}", "codigo_abreviado": codigo_existente}, headers=headers); assert resp_a.status_code == status.HTTP_201_CREATED
    resp_b = await client.post(url_base, json={"nombre": f"Fab Nom B {uuid.uuid4()}", "codigo_abreviado": f"COD-{uuid.uuid4().hex[:6]}"}, headers=headers); assert resp_b.status_code == status.HTTP_201_CREATED
    fab_b_id = resp_b.json()["id"]
    url_put = f"{FABRICANTES_PREFIX}/{fab_b_id}" # <-- URL Corregida
    response_update = await client.put(url_put, json={"codigo_abreviado": codigo_existente}, headers=headers); assert response_update.status_code == status.HTTP_409_CONFLICT

# ===== FIN DE tests/test_fabricantes_neumatico.py =====