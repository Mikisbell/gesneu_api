# tests/test_neumaticos.py (Corregido v2)
import pytest
import pytest_asyncio
import uuid
from datetime import date, datetime, timezone
from typing import Dict, Any, Tuple, Optional
from decimal import Decimal

from httpx import AsyncClient
from fastapi import status
from sqlmodel import select, SQLModel # Importar SQLModel base
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func

# --- Modelos, Schemas, Helpers, etc. ---
# (Asegúrate que todas estas importaciones sean correctas y existan)
from models.usuario import Usuario
from models.proveedor import Proveedor, TipoProveedorEnum
from models.fabricante import FabricanteNeumatico
from models.modelo import ModeloNeumatico
from models.neumatico import Neumatico, EstadoNeumaticoEnum
from models.almacen import Almacen
from models.evento_neumatico import EventoNeumatico, TipoEventoNeumaticoEnum
from models.vehiculo import Vehiculo


from models.tipo_vehiculo import TipoVehiculo                         # <-- Modelo desde tipo_vehiculo.py

from schemas.common import TipoEjeEnum, LadoVehiculoEnum # <-- Importar desde schemas           # <-- Enums desde common.py

from models.configuracion_eje import ConfiguracionEje
from models.posicion_neumatico import PosicionNeumatico
from models.motivo_desecho import MotivoDesecho
from models.parametro_inventario import ParametroInventario, TipoParametroEnum
from models.alerta import Alerta
# Schemas
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem
# Security & Core
from core.security import get_password_hash, create_access_token
from core.config import settings
# Helpers
from tests.helpers import create_user_and_get_token, get_or_create_almacen_test

API_PREFIX = settings.API_V1_STR
AUTH_PREFIX = f"{API_PREFIX}/auth"
NEUMATICOS_PREFIX = f"{API_PREFIX}/neumaticos"

# --- Funciones Helper (Asegúrate que estas funciones estén actualizadas) ---

async def setup_compra_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID]:
    """Crea usuario, token, fabricante, modelo, proveedor y almacén base."""
    user_password = f"pw_cpr_{uuid.uuid4().hex[:4]}"
    username = f"user_cpr_{uuid.uuid4().hex[:6]}"
    user = Usuario(username=username, password_hash=get_password_hash(user_password), activo=True, rol="OPERADOR")
    db_session.add(user); await db_session.commit(); await db_session.refresh(user)

    login_data = {"username": user.username, "password": user_password}
    token_url = f"{AUTH_PREFIX}/token"
    response_token = await client.post(token_url, data=login_data)
    assert response_token.status_code == status.HTTP_200_OK, f"Helper setup_compra: Failed token {response_token.text}"
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    fab = FabricanteNeumatico(nombre=f"Fab CPR {uuid.uuid4().hex[:4]}", codigo_abreviado=f"FCR{uuid.uuid4().hex[:4]}", activo=True, creado_por=user.id)
    db_session.add(fab); await db_session.commit(); await db_session.refresh(fab)
    
    modelo = ModeloNeumatico(
        fabricante_id=fab.id,
        nombre_modelo=f"Mod CPR {uuid.uuid4().hex[:4]}",
        medida="TEST",
        profundidad_original_mm=18.0,
        # --- AÑADIR/MODIFICAR ESTAS LÍNEAS ---
        permite_reencauche=True,
        reencauches_maximos=2, # O el número que necesites
        # ------------------------------------
        creado_por=user.id
    )


    db_session.add(modelo); await db_session.commit(); await db_session.refresh(modelo)
    prov = Proveedor(nombre=f"Prov CPR {uuid.uuid4().hex[:4]}", tipo=TipoProveedorEnum.DISTRIBUIDOR, activo=True, rfc=f"PCR{uuid.uuid4().hex[:6]}", creado_por=user.id)
    db_session.add(prov); await db_session.commit(); await db_session.refresh(prov)
    almacen = await get_or_create_almacen_test(db_session)

    return headers, modelo.id, prov.id, almacen.id, user.id


async def setup_instalacion_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Crea neumático EN_STOCK, vehículo, posición y devuelve IDs + headers."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    serie_unica = f"SERIE-INSTPRE-{uuid.uuid4().hex[:8]}"
    neum = Neumatico( numero_serie=serie_unica, modelo_id=modelo_id, fecha_compra=date.today(), costo_compra=500.00, proveedor_compra_id=proveedor_id, estado_actual=EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id=almacen_id, creado_por=user_id)
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)

    tipo_veh = TipoVehiculo(nombre=f"Tipo InstPre {uuid.uuid4().hex[:4]}", ejes_standard=1, categoria_principal="TEST", activo=True, creado_por=user_id)
    db_session.add(tipo_veh); await db_session.commit(); await db_session.refresh(tipo_veh)
    vehiculo = Vehiculo(numero_economico=f"ECO-INSTPRE-{uuid.uuid4().hex[:4]}", tipo_vehiculo_id=tipo_veh.id, activo=True, creado_por=user_id)
    db_session.add(vehiculo); await db_session.commit(); await db_session.refresh(vehiculo)
    config_eje = ConfiguracionEje(tipo_vehiculo_id=tipo_veh.id, numero_eje=1, nombre_eje="Eje Test InstPre", tipo_eje=TipoEjeEnum.TRACCION, numero_posiciones=1, neumaticos_por_posicion=1)
    db_session.add(config_eje); await db_session.commit(); await db_session.refresh(config_eje)
    posicion = PosicionNeumatico(configuracion_eje_id=config_eje.id, codigo_posicion=f"E1P1-IP{uuid.uuid4().hex[:2]}", lado=LadoVehiculoEnum.IZQUIERDO, posicion_relativa=1, es_direccion=False)
    db_session.add(posicion); await db_session.commit(); await db_session.refresh(posicion)

    return headers, neum.id, vehiculo.id, posicion.id


async def get_or_create_proveedor_reparacion(db_session: AsyncSession) -> Proveedor:
    nombre_prov = "Taller Reparacion Test General V2"
    stmt = select(Proveedor).where(Proveedor.nombre == nombre_prov)
    proveedor = (await db_session.exec(stmt)).first()
    if not proveedor:
        proveedor = Proveedor(nombre=nombre_prov, tipo=TipoProveedorEnum.SERVICIO_REPARACION, activo=True, rfc=f"TRTG2{uuid.uuid4().hex[:6]}")
        db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    elif proveedor.tipo != TipoProveedorEnum.SERVICIO_REPARACION or not proveedor.activo:
         proveedor.tipo = TipoProveedorEnum.SERVICIO_REPARACION; proveedor.activo = True
         db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    return proveedor

async def get_or_create_proveedor_reencauche(db_session: AsyncSession) -> Proveedor:
    nombre_prov = "Reencauchadora Test General V2"
    stmt = select(Proveedor).where(Proveedor.nombre == nombre_prov)
    proveedor = (await db_session.exec(stmt)).first()
    if not proveedor:
        proveedor = Proveedor(nombre=nombre_prov, tipo=TipoProveedorEnum.SERVICIO_REENCAUCHE, activo=True, rfc=f"RTG2{uuid.uuid4().hex[:7]}")
        db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    elif proveedor.tipo != TipoProveedorEnum.SERVICIO_REENCAUCHE or not proveedor.activo:
         proveedor.tipo = TipoProveedorEnum.SERVICIO_REENCAUCHE; proveedor.activo = True
         db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    return proveedor

async def set_profundidad_minima_param(db_session: AsyncSession, modelo_id: uuid.UUID, umbral: float) -> ParametroInventario:
    stmt = select(ParametroInventario).where(ParametroInventario.tipo_parametro == TipoParametroEnum.PROFUNDIDAD_MINIMA, ParametroInventario.modelo_id == modelo_id, ParametroInventario.almacen_id.is_(None))
    parametro = (await db_session.exec(stmt)).first()
    if parametro:
        parametro.valor_numerico = umbral
        parametro.activo = True
    else:
        parametro = ParametroInventario(tipo_parametro=TipoParametroEnum.PROFUNDIDAD_MINIMA, modelo_id=modelo_id, valor_numerico=umbral, activo=True)
    db_session.add(parametro); await db_session.commit(); await db_session.refresh(parametro)
    return parametro

# --- Inicio de los Tests ---

@pytest.mark.asyncio
async def test_crear_evento_compra_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento COMPRA."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    numero_serie_nuevo = f"SERIE-COMPRA-{uuid.uuid4().hex[:8]}"
    fecha_compra = date(2025, 5, 4)
    costo = Decimal("550.75")

    evento_payload = {
        "tipo_evento": TipoEventoNeumaticoEnum.COMPRA.value,
        "numero_serie": numero_serie_nuevo,
        "modelo_id": str(modelo_id),
        "fecha_compra": fecha_compra.isoformat(),
        "costo_compra": float(costo), # Enviar como float si el schema espera float
        "proveedor_compra_id": str(proveedor_id),
        "destino_almacen_id": str(almacen_id),
        "notas": "Compra test corregida",
    }
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED, f"Status={response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data and "neumatico_id" in data
    evento_id = uuid.UUID(data["id"])
    neumatico_creado_id = uuid.UUID(data["neumatico_id"])

    evento_db = await db_session.get(EventoNeumatico, evento_id)
    neumatico_db = await db_session.get(Neumatico, neumatico_creado_id)
    assert evento_db and neumatico_db
    assert neumatico_db.numero_serie == numero_serie_nuevo
    assert neumatico_db.estado_actual == EstadoNeumaticoEnum.EN_STOCK


@pytest.mark.asyncio
async def test_crear_evento_instalacion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento INSTALACION."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    odometro_instalacion = 12345
    fecha_ev = date(2025, 5, 1)
    evento_payload = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSTALACION.value,
        "vehiculo_id": str(vehiculo_id),
        "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": odometro_instalacion,
        "fecha_evento": fecha_ev.isoformat(), # Enviar fecha
        # Otros campos opcionales
        "profundidad_remanente_mm": 18.0,
        "presion_psi": 115.0
    }
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED, f"Install failed: {response.text}"

    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.INSTALADO
    assert neumatico_despues.ubicacion_actual_vehiculo_id == vehiculo_id
    assert neumatico_despues.ubicacion_actual_posicion_id == posicion_id
    assert neumatico_despues.km_instalacion == odometro_instalacion
    assert neumatico_despues.fecha_instalacion == fecha_ev


@pytest.mark.asyncio
async def test_crear_evento_desmontaje_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento DESMONTAJE a EN_STOCK."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # Instalar primero
    odometro_instalacion = 5000
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await client.post(url_eventos, json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": odometro_instalacion
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"
    await db_session.commit()

    neumatico_instalado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_instalado and neumatico_instalado.estado_actual == EstadoNeumaticoEnum.INSTALADO

    almacen_destino = await get_or_create_almacen_test(db_session)
    destino = EstadoNeumaticoEnum.EN_STOCK
    odometro_desmontaje = 10000

    evento_desmontaje_payload = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESMONTAJE.value,
        "motivo_desmontaje_destino": destino.value, # Nombre corregido en schema
        "odometro_vehiculo_en_evento": odometro_desmontaje,
        "destino_almacen_id": str(almacen_destino.id) # Requerido para EN_STOCK
    }
    response = await client.post(url_eventos, json=evento_desmontaje_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Desmontaje failed: {response.text}"
    await db_session.commit()

    await db_session.refresh(neumatico_instalado)
    assert neumatico_instalado.estado_actual == destino
    assert neumatico_instalado.ubicacion_almacen_id == almacen_destino.id
    # Línea corregida
    assert neumatico_instalado.kilometraje_acumulado == (odometro_desmontaje - odometro_instalacion)


@pytest.mark.asyncio
async def test_crear_evento_desecho_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento DESECHO desde EN_STOCK."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    serie_desecho = f"SERIE-DESECHO-{uuid.uuid4().hex[:8]}"
    neumatico_a_desechar = Neumatico( numero_serie=serie_desecho, modelo_id=modelo_id, fecha_compra=date.today(), costo_compra=100.0, proveedor_compra_id=proveedor_id, estado_actual=EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id=almacen_id, creado_por=user_id)
    db_session.add(neumatico_a_desechar); await db_session.commit(); await db_session.refresh(neumatico_a_desechar)
    neumatico_id = neumatico_a_desechar.id

    motivo = MotivoDesecho(codigo=f"TEST_DSCH_{uuid.uuid4().hex[:6]}", descripcion="Test Desecho")
    db_session.add(motivo); await db_session.commit(); await db_session.refresh(motivo)

    evento_desecho_payload = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESECHO.value,
        "motivo_desecho_id_evento": str(motivo.id),
    }
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_desecho_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Desecho failed: {response.text}"
    await db_session.commit()

    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues and neumatico_despues.estado_actual == EstadoNeumaticoEnum.DESECHADO


@pytest.mark.asyncio
async def test_crear_evento_desecho_fallido_si_instalado(client: AsyncClient, db_session: AsyncSession):
    """Prueba que DESECHO falla si el neumático está INSTALADO."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await client.post(url_eventos, json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": 1000
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"
    await db_session.commit()

    motivo = MotivoDesecho(codigo=f"TEST_DSCH_FAIL_{uuid.uuid4().hex[:6]}", descripcion="Test Desecho Fallido")
    db_session.add(motivo); await db_session.commit(); await db_session.refresh(motivo)

    evento_desecho_payload = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESECHO.value,
        "motivo_desecho_id_evento": str(motivo.id),
    }
    response = await client.post(url_eventos, json=evento_desecho_payload, headers=headers)
    # Espera ConflictError (409) según la lógica del servicio
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "No se puede desechar" in response.json()["detail"]


@pytest.mark.asyncio
async def test_leer_historial_neumatico_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /{neumatico_id}/historial."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    url_historial = f"{NEUMATICOS_PREFIX}/{neumatico_id}/historial"

    # Registrar eventos
    resp1 = await client.post(url_eventos, json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": 1000
    }, headers=headers)
    assert resp1.status_code == status.HTTP_201_CREATED
    await db_session.commit()
    evento1_id = resp1.json()["id"]

    resp2 = await client.post(url_eventos, json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSPECCION",
        "odometro_vehiculo_en_evento": 5000, "profundidad_remanente_mm": 17.0
    }, headers=headers)
    assert resp2.status_code == status.HTTP_201_CREATED
    await db_session.commit()
    evento2_id = resp2.json()["id"]

    # Solicitar historial
    response = await client.get(url_historial, headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"GET Historial failed: {response.text}"

    historial = response.json()
    assert isinstance(historial, list)
    ids_en_historial = {item["id"] for item in historial}
    assert evento1_id in ids_en_historial
    assert evento2_id in ids_en_historial
    assert historial[0]["id"] == evento2_id # Verificar orden


@pytest.mark.asyncio
async def test_crear_evento_desmontaje_fallido_sin_destino(client: AsyncClient, db_session: AsyncSession):
    """Prueba que DESMONTAJE falla (422) si no se envía motivo_desmontaje_destino."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # Instalar primero
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await client.post(url_eventos, json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": 500
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"
    await db_session.commit()

    evento_desmontaje_payload_incompleto = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESMONTAJE.value,
        "odometro_vehiculo_en_evento": 1000,
        # Falta motivo_desmontaje_destino
    }
    response = await client.post(url_eventos, json=evento_desmontaje_payload_incompleto, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "motivo_desmontaje_destino requerido." in response.json()["detail"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_leer_neumaticos_instalados_success(
    integration_client: AsyncClient, postgres_session: AsyncSession
):
    # ... (Mantener el código corregido de esta prueba como estaba) ...
    """Prueba GET /instalados contra PostgreSQL."""
    print("\n--- Iniciando test_leer_neumaticos_instalados_success (Integración) ---")
    user_suffix = uuid.uuid4().hex[:6]
    user_id_str, headers = await create_user_and_get_token(integration_client, postgres_session, f"inst_integ_{user_suffix}")
    user_id = uuid.UUID(user_id_str)
    # ... (Crear dependencias: Fab, Mod, Prov, Alm) ...
    test_suffix = uuid.uuid4().hex[:4]
    fab = FabricanteNeumatico(nombre=f"Fab Integ {test_suffix}", codigo_abreviado=f"FI{test_suffix}", activo=True, creado_por=user_id)
    postgres_session.add(fab); await postgres_session.commit(); await postgres_session.refresh(fab)
    modelo = ModeloNeumatico(fabricante_id=fab.id, nombre_modelo=f"Mod Integ {test_suffix}", medida="11R22.5", profundidad_original_mm=20.0, permite_reencauche=True, reencauches_maximos=2, creado_por=user_id)
    postgres_session.add(modelo); await postgres_session.commit(); await postgres_session.refresh(modelo)
    prov = Proveedor(nombre=f"Prov Integ {test_suffix}", tipo=TipoProveedorEnum.DISTRIBUIDOR, activo=True, creado_por=user_id)
    postgres_session.add(prov); await postgres_session.commit(); await postgres_session.refresh(prov)
    almacen = Almacen(codigo=f"ALMINT{test_suffix}", nombre="Almacen Integracion", activo=True, creado_por=user_id)
    postgres_session.add(almacen); await postgres_session.commit(); await postgres_session.refresh(almacen)
    # Crear Neumático
    neumatico_a_instalar = Neumatico(numero_serie=f"SERIE-INTEG-{test_suffix}", modelo_id=modelo.id, fecha_compra=date.today(), costo_compra=600.0, proveedor_compra_id=prov.id, estado_actual=EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id=almacen.id, creado_por=user_id)
    postgres_session.add(neumatico_a_instalar); await postgres_session.commit(); await postgres_session.refresh(neumatico_a_instalar)
    neumatico_id = neumatico_a_instalar.id
    # Crear Vehículo y Posición
    tipo_vehiculo = TipoVehiculo(nombre=f"TipoV Integ {test_suffix}", ejes_standard=2, categoria_principal="CAMIÓN", activo=True, creado_por=user_id)
    postgres_session.add(tipo_vehiculo); await postgres_session.commit(); await postgres_session.refresh(tipo_vehiculo)
    vehiculo = Vehiculo(numero_economico=f"ECO-INTEG-{test_suffix}", tipo_vehiculo_id=tipo_vehiculo.id, activo=True, creado_por=user_id)
    postgres_session.add(vehiculo); await postgres_session.commit(); await postgres_session.refresh(vehiculo)
    vehiculo_id = vehiculo.id
    config_eje = ConfiguracionEje(tipo_vehiculo_id=tipo_vehiculo.id, numero_eje=1, nombre_eje="Delantero Integ", tipo_eje=TipoEjeEnum.DIRECCION, numero_posiciones=2, neumaticos_por_posicion=1)
    postgres_session.add(config_eje); await postgres_session.commit(); await postgres_session.refresh(config_eje)
    posicion = PosicionNeumatico(configuracion_eje_id=config_eje.id, codigo_posicion=f"1LI-I{test_suffix}", lado=LadoVehiculoEnum.IZQUIERDO, posicion_relativa=1, es_direccion=True)
    postgres_session.add(posicion); await postgres_session.commit(); await postgres_session.refresh(posicion)
    posicion_id = posicion.id
    # Instalar vía API
    evento_instalacion = {"neumatico_id": str(neumatico_id), "tipo_evento": TipoEventoNeumaticoEnum.INSTALACION.value, "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id), "odometro_vehiculo_en_evento": 1000}
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await integration_client.post(url_eventos, json=evento_instalacion, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Setup install failed: {response_install.text}"
    await postgres_session.commit() # Commit después de la llamada API
    # Verificar estado en BD
    await postgres_session.refresh(neumatico_a_instalar)
    assert neumatico_a_instalar.estado_actual == EstadoNeumaticoEnum.INSTALADO
    # Llamar al endpoint /instalados
    url_instalados = f"{NEUMATICOS_PREFIX}/instalados"
    response = await integration_client.get(url_instalados, headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"GET /instalados failed: {response.text}"
    # Verificar respuesta
    instalados_data = response.json()
    assert isinstance(instalados_data, list)
    neumatico_encontrado = next((item for item in instalados_data if item.get("id") == str(neumatico_id)), None)
    assert neumatico_encontrado is not None
    assert neumatico_encontrado["numero_serie"] == neumatico_a_instalar.numero_serie


@pytest.mark.asyncio
async def test_crear_evento_inspeccion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento INSPECCION (CORREGIDO: instala primero)."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # Instalar
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    resp_inst = await client.post(url_eventos, json={"neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION", "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id), "odometro_vehiculo_en_evento": 1000}, headers=headers)
    assert resp_inst.status_code == status.HTTP_201_CREATED, f"Setup install failed: {resp_inst.text}"
    await db_session.commit()

    # Inspeccionar
    evento_inspeccion_payload = {"neumatico_id": str(neumatico_id), "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value, "profundidad_remanente_mm": 8.5, "presion_psi": 105.0, "odometro_vehiculo_en_evento": 1500}
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp failed: {response.text}"
    # ... (verificar datos si es necesario) ...


@pytest.mark.asyncio
async def test_crear_evento_rotacion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento ROTACION."""
    headers, neumatico_id, vehiculo_id, posicion1_id = await setup_instalacion_prerequisites(client, db_session)

    # Instalar
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    odometro_instalacion = 20000
    resp_inst = await client.post(url_eventos, json={"neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION", "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion1_id), "odometro_vehiculo_en_evento": odometro_instalacion}, headers=headers)
    assert resp_inst.status_code == status.HTTP_201_CREATED, f"Install setup failed: {resp_inst.text}"
    await db_session.commit()

    # Crear Posición 2
    pos1_db = await db_session.get(PosicionNeumatico, posicion1_id)
    config_eje1 = await db_session.get(ConfiguracionEje, pos1_db.configuracion_eje_id)
    codigo_pos2 = f"E{config_eje1.numero_eje}P2-T{uuid.uuid4().hex[:2]}"
    posicion_destino = PosicionNeumatico(configuracion_eje_id=config_eje1.id, codigo_posicion=codigo_pos2, lado=LadoVehiculoEnum.DERECHO, posicion_relativa=2, es_direccion=pos1_db.es_direccion)
    db_session.add(posicion_destino); await db_session.commit(); await db_session.refresh(posicion_destino)

    # Rotar
    odometro_rotacion = 25000
    evento_rotacion_payload = {"neumatico_id": str(neumatico_id), "tipo_evento": TipoEventoNeumaticoEnum.ROTACION.value, "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_destino.id), "odometro_vehiculo_en_evento": odometro_rotacion}
    response = await client.post(url_eventos, json=evento_rotacion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rotation failed: {response.text}"
    await db_session.commit()

    neumatico_rotado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_rotado and neumatico_rotado.ubicacion_actual_posicion_id == posicion_destino.id


@pytest.mark.asyncio
async def test_crear_evento_reparacion_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_ENTRADA."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    serie_rep_ent = f"SERIE-REPENT-{uuid.uuid4().hex[:8]}"
    neum = Neumatico( numero_serie=serie_rep_ent, modelo_id=modelo_id, fecha_compra=date.today(), costo_compra=1.0, proveedor_compra_id=proveedor_id, estado_actual=EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id=almacen_id, creado_por=user_id)
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)

    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    evento_payload = {"neumatico_id": str(neum.id), "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_ENTRADA.value, "proveedor_servicio_id": str(proveedor_reparacion.id)}
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Ent failed: {response.text}"
    await db_session.commit()

    neumatico_en_rep = await db_session.get(Neumatico, neum.id)
    assert neumatico_en_rep and neumatico_en_rep.estado_actual == EstadoNeumaticoEnum.EN_REPARACION


@pytest.mark.asyncio
async def test_crear_evento_reparacion_salida_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_SALIDA."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    serie_rep_sal = f"SERIE-REPSAL-{uuid.uuid4().hex[:8]}"
    neum = Neumatico( numero_serie=serie_rep_sal, modelo_id=modelo_id, fecha_compra=date.today(), costo_compra=1.0, proveedor_compra_id=proveedor_id, estado_actual=EstadoNeumaticoEnum.EN_REPARACION, creado_por=user_id)
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)

    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    almacen_destino = await get_or_create_almacen_test(db_session)

    evento_payload = {"neumatico_id": str(neum.id), "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_SALIDA.value, "proveedor_servicio_id": str(proveedor_reparacion.id), "destino_almacen_id": str(almacen_destino.id)}
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Sal failed: {response.text}"
    await db_session.commit()

    neumatico_reparado = await db_session.get(Neumatico, neum.id)
    assert neumatico_reparado and neumatico_reparado.estado_actual == EstadoNeumaticoEnum.EN_STOCK


@pytest.mark.asyncio
async def test_crear_evento_reencauche_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REENCAUCHE_ENTRADA."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    serie_reen_ent = f"SERIE-REENENT-{uuid.uuid4().hex[:8]}"
    neum = Neumatico( numero_serie=serie_reen_ent, modelo_id=modelo_id, fecha_compra=date.today(), costo_compra=1.0, proveedor_compra_id=proveedor_id, estado_actual=EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id=almacen_id, creado_por=user_id)
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)

    proveedor_reencauche = await get_or_create_proveedor_reencauche(db_session)
    evento_payload = {"neumatico_id": str(neum.id), "tipo_evento": TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA.value, "proveedor_servicio_id": str(proveedor_reencauche.id)}
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Reen Ent failed: {response.text}"
    await db_session.commit()

    neumatico_en_reenc = await db_session.get(Neumatico, neum.id)
    assert neumatico_en_reenc and neumatico_en_reenc.estado_actual == EstadoNeumaticoEnum.EN_REENCAUCHE


@pytest.mark.asyncio
async def test_crear_evento_reencauche_salida_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REENCAUCHE_SALIDA."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    serie_reen_sal = f"SERIE-REENSAL-{uuid.uuid4().hex[:8]}"
    neum = Neumatico(numero_serie=serie_reen_sal, modelo_id=modelo_id, fecha_compra=date.today(), costo_compra=1.0, proveedor_compra_id=proveedor_id, estado_actual=EstadoNeumaticoEnum.EN_REENCAUCHE, creado_por=user_id)
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)

    proveedor_reencauche = await get_or_create_proveedor_reencauche(db_session)
    almacen_destino = await get_or_create_almacen_test(db_session)
    profundidad_nueva = 16.0

    evento_payload = {"neumatico_id": str(neum.id), "tipo_evento": TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA.value, "proveedor_servicio_id": str(proveedor_reencauche.id), "profundidad_post_reencauche_mm": profundidad_nueva, "destino_almacen_id": str(almacen_destino.id)}
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Reen Sal failed: {response.text}"
    await db_session.commit()

    neumatico_despues = await db_session.get(Neumatico, neum.id)
    assert neumatico_despues and neumatico_despues.estado_actual == EstadoNeumaticoEnum.EN_STOCK


@pytest.mark.asyncio
async def test_crear_evento_ajuste_inventario_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento AJUSTE_INVENTARIO."""
    headers, modelo_id, proveedor_id, almacen_id, user_id = await setup_compra_prerequisites(client, db_session)
    serie_ajuste = f"SERIE-AJUSTE-{uuid.uuid4().hex[:8]}"
    neum = Neumatico( numero_serie=serie_ajuste, modelo_id=modelo_id, fecha_compra=date.today(), costo_compra=1.0, proveedor_compra_id=proveedor_id, estado_actual=EstadoNeumaticoEnum.EN_REPARACION, creado_por=user_id)
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)

    almacen_destino_ajuste = await get_or_create_almacen_test(db_session)
    estado_final_ajuste = EstadoNeumaticoEnum.EN_STOCK

    evento_payload = {
        "neumatico_id": str(neum.id),
        "tipo_evento": TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO.value,
        "estado_ajuste": estado_final_ajuste.value, # Campo requerido
        "destino_almacen_id": str(almacen_destino_ajuste.id) # Campo requerido
    }
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Ajuste Inv failed: {response.text}"
    await db_session.commit()

    neumatico_ajustado = await db_session.get(Neumatico, neum.id)
    assert neumatico_ajustado and neumatico_ajustado.estado_actual == estado_final_ajuste


@pytest.mark.asyncio
async def test_evento_inspeccion_genera_alerta_profundidad_baja(client: AsyncClient, db_session: AsyncSession):
    """Verifica que INSPECCION con profundidad < umbral genera alerta (CORREGIDO)."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    modelo_id = neumatico.modelo_id
    umbral_minimo = 5.0
    await set_profundidad_minima_param(db_session, modelo_id, umbral_minimo)

    # Instalar
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    resp_inst = await client.post(url_eventos, json={"neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION", "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id), "odometro_vehiculo_en_evento": 1000}, headers=headers)
    assert resp_inst.status_code == status.HTTP_201_CREATED, f"Setup install failed: {resp_inst.text}"
    await db_session.commit()

    # Inspeccionar con profundidad baja
    profundidad_medida = 4.0
    evento_inspeccion_payload = {"neumatico_id": str(neumatico_id), "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value, "profundidad_remanente_mm": profundidad_medida, "odometro_vehiculo_en_evento": 1500}
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp Baja failed: {response.text}"
    await db_session.commit()

    # Verificar alerta
    stmt_alerta = select(Alerta).where(Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA', Alerta.neumatico_id == neumatico_id, Alerta.estado_alerta != 'GESTIONADA')
    alertas = (await db_session.exec(stmt_alerta)).all()
    assert len(alertas) >= 1, "No se generó alerta PROFUNDIDAD_BAJA activa"


@pytest.mark.asyncio
async def test_evento_inspeccion_no_genera_alerta_profundidad_ok(client: AsyncClient, db_session: AsyncSession):
    """Verifica que INSPECCION con profundidad >= umbral NO genera alerta (CORREGIDO)."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    modelo_id = neumatico.modelo_id
    await set_profundidad_minima_param(db_session, modelo_id, 5.0)

    # Instalar
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    resp_inst = await client.post(url_eventos, json={"neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION", "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id), "odometro_vehiculo_en_evento": 1000}, headers=headers)
    assert resp_inst.status_code == status.HTTP_201_CREATED, f"Setup install failed: {resp_inst.text}"
    await db_session.commit()

    # Contar alertas ANTES
    stmt_count_before = select(func.count(Alerta.id)).where(Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA', Alerta.neumatico_id == neumatico_id, Alerta.estado_alerta != 'GESTIONADA')
    count_before = await db_session.scalar(stmt_count_before) or 0

    # Inspeccionar OK
    evento_inspeccion_payload = {"neumatico_id": str(neumatico_id), "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value, "profundidad_remanente_mm": 6.0, "odometro_vehiculo_en_evento": 1500}
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp OK failed: {response.text}"
    await db_session.commit()

    # Contar alertas DESPUÉS
    stmt_count_after = select(func.count(Alerta.id)).where(Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA', Alerta.neumatico_id == neumatico_id, Alerta.estado_alerta != 'GESTIONADA')
    count_after = await db_session.scalar(stmt_count_after) or 0
    assert count_after == count_before, "Se generó/mantuvo alerta inesperada para profundidad OK"


@pytest.mark.asyncio
async def test_evento_inspeccion_no_genera_alerta_sin_profundidad(client: AsyncClient, db_session: AsyncSession):
    """Verifica que INSPECCION sin dato de profundidad NO genera alerta (CORREGIDO)."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    await set_profundidad_minima_param(db_session, neumatico.modelo_id, 5.0)

    # Instalar
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    resp_inst = await client.post(url_eventos, json={"neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION", "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id), "odometro_vehiculo_en_evento": 1000}, headers=headers)
    assert resp_inst.status_code == status.HTTP_201_CREATED, f"Setup install failed: {resp_inst.text}"
    await db_session.commit()

    # Contar alertas ANTES
    stmt_count_before = select(func.count(Alerta.id)).where(Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA', Alerta.neumatico_id == neumatico_id, Alerta.estado_alerta != 'GESTIONADA')
    count_before = await db_session.scalar(stmt_count_before) or 0

    # Inspeccionar SIN profundidad
    evento_inspeccion_payload = {"neumatico_id": str(neumatico_id), "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value, "presion_psi": 110.0, "odometro_vehiculo_en_evento": 1500}
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp sin prof failed: {response.text}"
    await db_session.commit()

    # Contar alertas DESPUÉS
    stmt_count_after = select(func.count(Alerta.id)).where(Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA', Alerta.neumatico_id == neumatico_id, Alerta.estado_alerta != 'GESTIONADA')
    count_after = await db_session.scalar(stmt_count_after) or 0
    assert count_after == count_before, "Se generó alerta inesperada para inspección sin profundidad"