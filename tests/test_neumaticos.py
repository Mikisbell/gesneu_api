# tests/test_neumaticos.py MIKIS FALTA CORREGIR
import pytest
import pytest_asyncio
import uuid
from datetime import date, datetime, timezone # Asegurar timezone
from typing import Dict, Any, Tuple, Optional
from decimal import Decimal # Importar Decimal para comparaciones precisas

from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func # <-- Importación añadida

# Importar modelos, schemas y helpers necesarios
from models.usuario import Usuario
from models.proveedor import Proveedor
from models.fabricante import FabricanteNeumatico
from models.modelo import ModeloNeumatico
from models.neumatico import Neumatico, EstadoNeumaticoEnum # Importante
from models.almacen import Almacen # Importación añadida
from models.evento_neumatico import EventoNeumatico # Para verificar en BD
from models.vehiculo import Vehiculo
from models.tipo_vehiculo import TipoVehiculo
from models.configuracion_eje import ConfiguracionEje
from models.posicion_neumatico import PosicionNeumatico
from schemas.common import LadoVehiculoEnum, TipoEjeEnum # EstadoNeumaticoEnum ya importado
from models.motivo_desecho import MotivoDesecho
from schemas.common import TipoProveedorEnum # Asegúrate que esté importado
from models.parametro_inventario import ParametroInventario
from models.alerta import Alerta
# Schemas
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem
from schemas.common import TipoEventoNeumaticoEnum, LadoVehiculoEnum, TipoEjeEnum, TipoProveedorEnum
from schemas.common import TipoParametroEnum # <-- ¡IMPORTANTE IMPORTAR EL ENUM!
# Security & Core
from core.security import get_password_hash # Necesario para el helper
from core.security import create_access_token, get_password_hash
# Helpers (Asume que existe tests/helpers.py)
from tests.helpers import create_user_and_get_token
# Security & Core
from core.config import settings
API_PREFIX = settings.API_V1_STR
AUTH_PREFIX = f"{API_PREFIX}/auth"
# También es buena idea definir el prefijo específico para neumáticos
NEUMATICOS_PREFIX = f"{API_PREFIX}/neumaticos"
# --- Funciones Helper (Asegúrate que estas funciones helper estén definidas como las tenías) ---
async def get_or_create_almacen_test(session: AsyncSession) -> Almacen:
    """Obtiene o crea un almacén para pruebas."""
    stmt = select(Almacen).where(Almacen.codigo == "ALMTEST")
    res = await session.exec(stmt)
    almacen = res.first()
    if not almacen:
        almacen = Almacen(codigo="ALMTEST", nombre="Almacén de Test", activo=True)
        session.add(almacen)
        await session.commit()
        await session.refresh(almacen)
    elif not almacen.activo:
        almacen.activo = True
        session.add(almacen)
        await session.commit()
        await session.refresh(almacen)
    return almacen

async def setup_compra_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID]:
    """Crea neumático base y dependencias (usuario, token, fab, mod, prov)."""
    user_password = f"password_neum_compra_{uuid.uuid4().hex[:4]}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_neum_compra_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    user = Usuario(username=username, email=email, password_hash=hashed_password, activo=True, rol="OPERADOR")
    db_session.add(user); await db_session.commit(); await db_session.refresh(user)

    login_data = {"username": user.username, "password": user_password}
    token_url = f"{AUTH_PREFIX}/token" # Usar el prefijo de Auth definido arriba
    response_token = await client.post(token_url, data=login_data)



    if response_token.status_code != status.HTTP_200_OK:
         pytest.fail(f"Fallo al obtener token en helper setup_compra: {response_token.text}")
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Crear Fabricante si no existe uno genérico
    fab_nombre = "Test Fab Compra General"
    stmt_fab = select(FabricanteNeumatico).where(FabricanteNeumatico.nombre == fab_nombre)
    fab = (await db_session.exec(stmt_fab)).first()
    if not fab:
        fab = FabricanteNeumatico(nombre=fab_nombre, activo=True, codigo_abreviado=f"TFCG{uuid.uuid4().hex[:4]}")
        db_session.add(fab); await db_session.commit(); await db_session.refresh(fab)

    # Crear Modelo si no existe uno genérico para el fabricante
    modelo_nombre = "Test Mod Compra General"
    stmt_mod = select(ModeloNeumatico).where(ModeloNeumatico.nombre_modelo == modelo_nombre, ModeloNeumatico.fabricante_id == fab.id)
    modelo = (await db_session.exec(stmt_mod)).first()
    if not modelo:
        modelo = ModeloNeumatico(
             fabricante_id=fab.id, nombre_modelo=modelo_nombre, medida="295/80R22.5",
             profundidad_original_mm=18.0, permite_reencauche=True, reencauches_maximos=2
        )
        db_session.add(modelo); await db_session.commit(); await db_session.refresh(modelo)

    # Crear Proveedor Compra si no existe uno genérico
    prov_nombre = "Test Prov Compra General"
    stmt_prov = select(Proveedor).where(Proveedor.nombre == prov_nombre)
    prov = (await db_session.exec(stmt_prov)).first()
    if not prov:
        prov = Proveedor(nombre=prov_nombre, tipo=TipoProveedorEnum.DISTRIBUIDOR, activo=True, rfc=f"TPCG{uuid.uuid4().hex[:7]}")
        db_session.add(prov); await db_session.commit(); await db_session.refresh(prov)

    # Crear Neumático con datos básicos y estado EN_STOCK
    serie_unica = f"SERIE-COMPRA-{uuid.uuid4().hex[:8]}"
    neum = Neumatico(
         numero_serie=serie_unica, modelo_id=modelo.id, fecha_compra=date.today(),
         costo_compra=500.00, proveedor_compra_id=prov.id,
         estado_actual=EstadoNeumaticoEnum.EN_STOCK # Asegurar estado inicial
         # ubicacion_almacen_id podría asignarse aquí si se conoce el almacén inicial
    )
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)

    return headers, neum.id, prov.id

async def setup_instalacion_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Crea neumático, vehículo, posición y dependencias para pruebas de instalación."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)

    # Asegurar que el neumático esté EN_STOCK
    neumatico_check = await db_session.get(Neumatico, neumatico_id)
    if neumatico_check and neumatico_check.estado_actual != EstadoNeumaticoEnum.EN_STOCK:
        neumatico_check.estado_actual = EstadoNeumaticoEnum.EN_STOCK
        neumatico_check.ubicacion_actual_vehiculo_id = None
        neumatico_check.ubicacion_actual_posicion_id = None
        # Asignar a un almacén de prueba si no está
        if not neumatico_check.ubicacion_almacen_id:
            almacen_test = await get_or_create_almacen_test(db_session)
            neumatico_check.ubicacion_almacen_id = almacen_test.id
        db_session.add(neumatico_check)
        await db_session.commit()
        await db_session.refresh(neumatico_check)
        print(f"WARN: Neumático {neumatico_id} forzado a EN_STOCK en helper de instalación.")

    # Crear Tipo Vehículo si no existe uno genérico
    tipo_veh_nombre = "Test Tipo Veh Instal General"
    stmt_tv = select(TipoVehiculo).where(TipoVehiculo.nombre == tipo_veh_nombre)
    tipo_vehiculo = (await db_session.exec(stmt_tv)).first()
    if not tipo_vehiculo:
        tipo_vehiculo = TipoVehiculo(nombre=tipo_veh_nombre, ejes_standard=3, categoria_principal="CAMIÓN", activo=True)
        db_session.add(tipo_vehiculo); await db_session.commit(); await db_session.refresh(tipo_vehiculo)

    # Crear Vehículo
    eco_unico_inst = f"ECO-INST-{uuid.uuid4().hex[:6]}"
    placa_unica_inst = f"INST-{uuid.uuid4().hex[:6].upper()}"
    vehiculo = Vehiculo(
         numero_economico=eco_unico_inst, placa=placa_unica_inst,
         tipo_vehiculo_id=tipo_vehiculo.id, activo=True
    )
    db_session.add(vehiculo); await db_session.commit(); await db_session.refresh(vehiculo)

    # Crear Config Eje si no existe para el tipo
    eje_num = 1
    stmt_ce = select(ConfiguracionEje).where(ConfiguracionEje.tipo_vehiculo_id == tipo_vehiculo.id, ConfiguracionEje.numero_eje == eje_num)
    config_eje = (await db_session.exec(stmt_ce)).first()
    if not config_eje:
        config_eje = ConfiguracionEje(
             tipo_vehiculo_id=tipo_vehiculo.id, numero_eje=eje_num, nombre_eje="Delantero Test",
             tipo_eje=TipoEjeEnum.DIRECCION, numero_posiciones=2, neumaticos_por_posicion=1
        )
        db_session.add(config_eje); await db_session.commit(); await db_session.refresh(config_eje)

    # Crear Posición si no existe para el eje
    codigo_pos_unico = f"E{config_eje.numero_eje}LI-T" # Código único para test
    stmt_pos = select(PosicionNeumatico).where(PosicionNeumatico.configuracion_eje_id == config_eje.id, PosicionNeumatico.codigo_posicion == codigo_pos_unico)
    posicion = (await db_session.exec(stmt_pos)).first()
    if not posicion:
        posicion = PosicionNeumatico(
             configuracion_eje_id=config_eje.id, codigo_posicion=codigo_pos_unico,
             lado=LadoVehiculoEnum.IZQUIERDO, posicion_relativa=1, es_direccion=True
        )
        db_session.add(posicion); await db_session.commit(); await db_session.refresh(posicion)

    return headers, neumatico_id, vehiculo.id, posicion.id


async def get_or_create_proveedor_reparacion(db_session: AsyncSession) -> Proveedor:
    """Obtiene o crea un proveedor de reparación genérico."""
    nombre_prov = "Taller Reparacion Test General"
    stmt = select(Proveedor).where(Proveedor.nombre == nombre_prov)
    result = await db_session.exec(stmt)
    proveedor = result.first()
    if not proveedor:
        proveedor = Proveedor(nombre=nombre_prov, tipo=TipoProveedorEnum.SERVICIO_REPARACION, activo=True, rfc=f"TRTG{uuid.uuid4().hex[:7]}")
        db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    elif proveedor.tipo != TipoProveedorEnum.SERVICIO_REPARACION or not proveedor.activo:
         proveedor.tipo = TipoProveedorEnum.SERVICIO_REPARACION; proveedor.activo = True
         db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    return proveedor

async def get_or_create_proveedor_reencauche(db_session: AsyncSession) -> Proveedor:
    """Obtiene o crea un proveedor de reencauche genérico."""
    nombre_prov = "Reencauchadora Test General"
    stmt = select(Proveedor).where(Proveedor.nombre == nombre_prov)
    result = await db_session.exec(stmt)
    proveedor = result.first()
    if not proveedor:
        proveedor = Proveedor(nombre=nombre_prov, tipo=TipoProveedorEnum.SERVICIO_REENCAUCHE, activo=True, rfc=f"RTG{uuid.uuid4().hex[:8]}")
        db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    elif proveedor.tipo != TipoProveedorEnum.SERVICIO_REENCAUCHE or not proveedor.activo:
         proveedor.tipo = TipoProveedorEnum.SERVICIO_REENCAUCHE; proveedor.activo = True
         db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    return proveedor

async def set_profundidad_minima_param(
    db_session: AsyncSession, modelo_id: uuid.UUID, umbral: float
) -> ParametroInventario:
    """Establece el parámetro PROFUNDIDAD_MINIMA para un modelo (CORREGIDO v2)."""
    # --- CORRECCIÓN EN LA COMPARACIÓN (tipo_parametro y almacen_id) ---
    stmt = select(ParametroInventario).where(
        ParametroInventario.tipo_parametro == TipoParametroEnum.PROFUNDIDAD_MINIMA, # <-- Comparar con el miembro del Enum
        ParametroInventario.modelo_id == modelo_id,
        ParametroInventario.almacen_id.is_(None) # <-- Usar el nombre de campo correcto 'almacen_id'
    )
    # --- FIN CORRECCIÓN ---
    result = await db_session.exec(stmt)
    parametro = result.first()
    if parametro:
        parametro.valor_numerico = umbral
        parametro.activo = True
    else:
        parametro = ParametroInventario(
            tipo_parametro=TipoParametroEnum.PROFUNDIDAD_MINIMA, # <-- Usar el miembro del Enum
            modelo_id=modelo_id,
            valor_numerico=umbral,
            activo=True
            # creado_por se podría añadir si se pasa current_user
        )
    db_session.add(parametro)
    await db_session.commit()
    await db_session.refresh(parametro)
    return parametro
# --- Fin Helper ---
# --- Inicio de los Tests ---
@pytest.mark.asyncio
async def test_crear_evento_compra_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento COMPRA."""
    headers, neumatico_id, proveedor_id = await setup_compra_prerequisites(client, db_session) # Asume que setup_... usa AUTH_PREFIX correctamente
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.COMPRA.value,
        "proveedor_servicio_id": str(proveedor_id),
        "costo_evento": 500.00,
        "moneda_costo": "PEN",
        "notas": "Evento de compra de prueba registrado",
    }
    # --- CORRECCIÓN ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Status esperado 201, obtenido {response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["neumatico_id"] == str(neumatico_id)
    assert data["tipo_evento"] == TipoEventoNeumaticoEnum.COMPRA.value
    evento_id = uuid.UUID(data["id"])
    evento_db = await db_session.get(EventoNeumatico, evento_id)
    assert evento_db is not None
    assert evento_db.tipo_evento == TipoEventoNeumaticoEnum.COMPRA

@pytest.mark.asyncio
async def test_crear_evento_instalacion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento INSTALACION."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    neumatico_antes = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_antes is not None
    assert neumatico_antes.estado_actual == EstadoNeumaticoEnum.EN_STOCK

    odometro_instalacion = 12345
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSTALACION.value,
        "vehiculo_id": str(vehiculo_id),
        "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": odometro_instalacion,
        "profundidad_remanente_mm": 15.5, # Profundidad al instalar
        "presion_psi": 110.0,
        "notas": "Evento de instalación de prueba",
    }

    # --- CORRECCIÓN AQUÍ ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos" # <-- Construye /api/v1/neumaticos/eventos
    response = await client.post(url_eventos, json=evento_payload, headers=headers) # <-- Usa la url_eventos
    # --- FIN CORRECCIÓN ---

    assert response.status_code == status.HTTP_201_CREATED, f"Install failed: {response.text}"

    # Verificar estado final del neumático volviendo a obtenerlo (get es más seguro post-commit)
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.INSTALADO
    assert neumatico_despues.ubicacion_actual_vehiculo_id == vehiculo_id
    assert neumatico_despues.ubicacion_actual_posicion_id == posicion_id
    assert neumatico_despues.ubicacion_almacen_id is None
    assert neumatico_despues.kilometraje_acumulado == 0
    assert neumatico_despues.fecha_ultimo_evento is not None

@pytest.mark.asyncio
async def test_crear_evento_desmontaje_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento DESMONTAJE a EN_STOCK."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session) # Asume que usa setup_compra_... corregido

    # --- CORRECCIÓN (URL para instalación dentro del test) ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": 5000
    }, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"

    neumatico_instalado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_instalado is not None
    assert neumatico_instalado.estado_actual == EstadoNeumaticoEnum.INSTALADO

    almacen_destino = await get_or_create_almacen_test(db_session)
    almacen_destino_id = almacen_destino.id
    assert almacen_destino_id is not None
    destino = EstadoNeumaticoEnum.EN_STOCK
    odometro_desmontaje = 10000

    evento_desmontaje_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESMONTAJE.value,
        "destino_desmontaje": destino.value,
        "odometro_vehiculo_en_evento": odometro_desmontaje,
        "profundidad_remanente_mm": 10.5,
        "notas": "Desmontaje a stock (test)",
        "almacen_destino_id": str(almacen_destino_id)
    }
    # --- CORRECCIÓN (URL para desmontaje) ---
    # url_eventos ya está definida arriba
    response = await client.post(url_eventos, json=evento_desmontaje_payload, headers=headers) # <-- Usa url_eventos
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Status esperado 201 para DESMONTAJE, obtenido {response.status_code}: {response.text}"

    await db_session.refresh(neumatico_instalado)
    neumatico_despues = neumatico_instalado
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == destino
    assert neumatico_despues.ubicacion_actual_vehiculo_id is None
    assert neumatico_despues.ubicacion_actual_posicion_id is None
    assert neumatico_despues.ubicacion_almacen_id == almacen_destino_id
    assert neumatico_despues.fecha_ultimo_evento is not None

@pytest.mark.asyncio
async def test_crear_evento_desecho_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento DESECHO desde EN_STOCK."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)

    motivo_codigo = f"TEST_DSCH_{uuid.uuid4().hex[:6]}"
    motivo = MotivoDesecho(codigo=motivo_codigo, descripcion="Test Desecho")
    db_session.add(motivo); await db_session.commit(); await db_session.refresh(motivo)
    motivo_id = motivo.id

    neumatico_antes = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_antes and neumatico_antes.estado_actual != EstadoNeumaticoEnum.INSTALADO

    evento_desecho_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESECHO.value,
        "motivo_desecho_id_evento": str(motivo_id),
        "profundidad_remanente_mm": 2.0,
    }
    # --- CORRECCIÓN ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_desecho_payload, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Desecho failed: {response.text}"

    await db_session.refresh(neumatico_antes)
    neumatico_despues = neumatico_antes
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.DESECHADO
    assert neumatico_despues.motivo_desecho_id == motivo_id
    assert neumatico_despues.fecha_desecho is not None
    assert neumatico_despues.ubicacion_almacen_id is None


@pytest.mark.asyncio
async def test_crear_evento_desecho_fallido_si_instalado(client: AsyncClient, db_session: AsyncSession):
    """Prueba que DESECHO falla si el neumático está INSTALADO."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # --- CORRECCIÓN (URL para instalación dentro del test) ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id)
    }, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"

    motivo = MotivoDesecho(codigo=f"TEST_DSCH_FAIL_{uuid.uuid4().hex[:6]}", descripcion="Test Desecho Fallido")
    db_session.add(motivo); await db_session.commit(); await db_session.refresh(motivo)
    motivo_id = motivo.id

    evento_desecho_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESECHO.value,
        "motivo_desecho_id_evento": str(motivo_id),
    }
    # --- CORRECCIÓN (URL para intento de desecho) ---
    # url_eventos ya definida arriba
    response = await client.post(url_eventos, json=evento_desecho_payload, headers=headers) # <-- Usa url_eventos
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "No se puede desechar un neumático INSTALADO" in response.text
    
@pytest.mark.asyncio
async def test_leer_historial_neumatico_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /{neumatico_id}/historial."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # --- CORRECCIÓN AQUÍ (También en las llamadas POST) ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos" # <-- Construye /api/v1/neumaticos/eventos
    url_historial = f"{NEUMATICOS_PREFIX}/{neumatico_id}/historial" # <-- Construye /api/v1/neumaticos/{id}/historial
    # --- FIN CORRECCIÓN ---

    # Registrar algunos eventos (usando url_eventos)
    resp1 = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id), "odometro_vehiculo_en_evento": 1000
    }, headers=headers)
    assert resp1.status_code == status.HTTP_201_CREATED
    evento1_id = resp1.json()["id"]

    resp2 = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSPECCION",
        "odometro_vehiculo_en_evento": 5000, "profundidad_remanente_mm": 17.0
    }, headers=headers)
    assert resp2.status_code == status.HTTP_201_CREATED
    evento2_id = resp2.json()["id"]

    # Solicitar historial (usando url_historial)
    response = await client.get(url_historial, headers=headers) # <-- Usa url_historial
    assert response.status_code == status.HTTP_200_OK, f"GET Historial failed: {response.text}"

    historial = response.json()
    assert isinstance(historial, list)
    assert len(historial) >= 2 # Al menos los dos eventos registrados
    ids_en_historial = {item["id"] for item in historial}
    assert evento1_id in ids_en_historial
    assert evento2_id in ids_en_historial

@pytest.mark.asyncio
async def test_crear_evento_desmontaje_fallido_sin_destino(client: AsyncClient, db_session: AsyncSession):
    """Prueba que DESMONTAJE falla (422) si no se envía destino_desmontaje."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # --- CORRECCIÓN (URL para instalación dentro del test) ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id)
    }, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"

    evento_desmontaje_payload_incompleto: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESMONTAJE.value,
        "odometro_vehiculo_en_evento": 10000,
    }
    # --- CORRECCIÓN (URL para intento de desmontaje) ---
    # url_eventos ya definida arriba
    response = await client.post(url_eventos, json=evento_desmontaje_payload_incompleto, headers=headers) # <-- Usa url_eventos
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "destino_desmontaje es requerido" in response.text
    

@pytest.mark.integration # Marcar como prueba de integración
@pytest.mark.asyncio
async def test_leer_neumaticos_instalados_success(
    integration_client: AsyncClient, # Usa el cliente configurado con PG
    postgres_session: AsyncSession # Usa la sesión PG
):
    """
    Prueba GET /instalados contra PostgreSQL, verificando la vista.
    Incluye verificación explícita del estado del neumático post-instalación.
    """
    print("\n--- Iniciando test_leer_neumaticos_instalados_success (Integración) ---")

    # --- 1. Setup: Crear datos necesarios en la BD de prueba Postgres ---
    print("Setup: Creando usuario y obteniendo token...")
    user_id_str, headers = await create_user_and_get_token(
        integration_client, postgres_session, "inst_integ_v3" # Cambiar sufijo si es necesario
    )
    user_id = uuid.UUID(user_id_str)
    print(f"Setup: Usuario {user_id} creado y token obtenido.")

    # Crear dependencias mínimas (Fabricante, Modelo, Proveedor, Almacen)
    print("Setup: Creando dependencias (Fabricante, Modelo, Proveedor, Almacen)...")
    test_suffix = uuid.uuid4().hex[:4]
    fabricante = FabricanteNeumatico(nombre=f"Fab Integ {test_suffix}", codigo_abreviado=f"FI{test_suffix}", activo=True, creado_por=user_id)
    postgres_session.add(fabricante)
    await postgres_session.commit()
    await postgres_session.refresh(fabricante)

    modelo = ModeloNeumatico(
        fabricante_id=fabricante.id, nombre_modelo=f"Mod Integ {test_suffix}", medida="11R22.5",
        profundidad_original_mm=20.0, permite_reencauche=True, reencauches_maximos=2, creado_por=user_id
    )
    postgres_session.add(modelo)
    await postgres_session.commit()
    await postgres_session.refresh(modelo)

    proveedor = Proveedor(nombre=f"Prov Integ {test_suffix}", tipo=TipoProveedorEnum.DISTRIBUIDOR, activo=True, creado_por=user_id)
    postgres_session.add(proveedor)
    await postgres_session.commit()
    await postgres_session.refresh(proveedor)

    almacen = Almacen(codigo=f"ALMINT{test_suffix}", nombre="Almacen Integracion", activo=True, creado_por=user_id)
    postgres_session.add(almacen)
    await postgres_session.commit()
    await postgres_session.refresh(almacen)
    print("Setup: Dependencias creadas.")

    # Crear Neumático en Stock
    print("Setup: Creando neumático...")
    neumatico_a_instalar = Neumatico(
        numero_serie=f"SERIE-INTEG-{test_suffix}", modelo_id=modelo.id,
        fecha_compra=date.today(), costo_compra=600.0, proveedor_compra_id=proveedor.id,
        estado_actual=EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id=almacen.id,
        creado_por=user_id
    )
    postgres_session.add(neumatico_a_instalar)
    await postgres_session.commit()
    await postgres_session.refresh(neumatico_a_instalar)
    neumatico_id = neumatico_a_instalar.id
    print(f"Setup: Neumático {neumatico_id} creado en estado EN_STOCK.")

    # Crear Vehículo, Tipo, Eje, Posición
    print("Setup: Creando Vehículo y Posiciones...")
    tipo_vehiculo = TipoVehiculo(nombre=f"TipoV Integ {test_suffix}", ejes_standard=2, categoria_principal="CAMIÓN", activo=True, creado_por=user_id)
    postgres_session.add(tipo_vehiculo)
    await postgres_session.commit()
    await postgres_session.refresh(tipo_vehiculo)

    vehiculo = Vehiculo(
        numero_economico=f"ECO-INTEG-{test_suffix}", tipo_vehiculo_id=tipo_vehiculo.id, activo=True, creado_por=user_id
    )
    postgres_session.add(vehiculo)
    await postgres_session.commit()
    await postgres_session.refresh(vehiculo)
    vehiculo_id = vehiculo.id

    config_eje = ConfiguracionEje(
        tipo_vehiculo_id=tipo_vehiculo.id, numero_eje=1, nombre_eje="Delantero Integ",
        tipo_eje=TipoEjeEnum.DIRECCION, numero_posiciones=2, neumaticos_por_posicion=1
    )
    postgres_session.add(config_eje)
    await postgres_session.commit()
    await postgres_session.refresh(config_eje)

    posicion = PosicionNeumatico(
        configuracion_eje_id=config_eje.id,
        codigo_posicion=f"1LI-I{test_suffix}", # 9 caracteres <= 10
        lado=LadoVehiculoEnum.IZQUIERDO,
        posicion_relativa=1,
        es_direccion=True
    )
    postgres_session.add(posicion)
    await postgres_session.commit()
    await postgres_session.refresh(posicion)
    posicion_id = posicion.id
    print("Setup: Vehículo y posición creados.")

    # Instalar el neumático usando el endpoint /eventos
    print(f"Setup: Instalando neumático {neumatico_id} en vehículo {vehiculo_id}...")
    evento_instalacion = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSTALACION.value,
        "vehiculo_id": str(vehiculo_id),
        "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": 1000,
        "profundidad_remanente_mm": modelo.profundidad_original_mm
    }

    # --- *** CORRECCIÓN DE URL *** ---
    # Construir la URL correcta usando el prefijo definido
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response_install = await integration_client.post(url_eventos, json=evento_instalacion, headers=headers)
    # --- *** FIN CORRECCIÓN *** ---

    assert response_install.status_code == status.HTTP_201_CREATED, f"Setup fallido: No se pudo instalar neumático vía API. Response: {response_install.text}"
    # Commit para asegurar que la transacción (incluyendo triggers) se complete
    # Nota: Podría no ser necesario si la fixture maneja la transacción
    await postgres_session.commit()
    print("Setup: Neumático instalado (llamada API y commit realizados).")

    # --- VERIFICACIÓN DIRECTA EN BD POST-INSTALACIÓN (Opcional pero útil) ---
    print(f"DEBUG: Verificando estado de neumático {neumatico_id} en BD post-instalación...")
    await postgres_session.refresh(neumatico_a_instalar) # Refrescar el objeto existente
    neumatico_verificado_db = neumatico_a_instalar # Usar el objeto refrescado
    assert neumatico_verificado_db is not None
    print(f"DEBUG: Estado actual leído de BD: {neumatico_verificado_db.estado_actual}")
    print(f"DEBUG: Ubicacion Almacen ID leído de BD: {neumatico_verificado_db.ubicacion_almacen_id}")
    print(f"DEBUG: Ubicacion Vehiculo ID leído de BD: {neumatico_verificado_db.ubicacion_actual_vehiculo_id}")
    print(f"DEBUG: Ubicacion Posicion ID leído de BD: {neumatico_verificado_db.ubicacion_actual_posicion_id}")
    assert neumatico_verificado_db.estado_actual == EstadoNeumaticoEnum.INSTALADO, f"DEBUG FALLIDO: Neumático {neumatico_id} no quedó en estado INSTALADO."
    assert neumatico_verificado_db.ubicacion_almacen_id is None, f"DEBUG FALLIDO: Neumático {neumatico_id} aún tiene ubicacion_almacen_id."
    assert neumatico_verificado_db.ubicacion_actual_vehiculo_id == vehiculo_id, "DEBUG FALLIDO: ubicacion_vehiculo incorrecta."
    assert neumatico_verificado_db.ubicacion_actual_posicion_id == posicion_id, "DEBUG FALLIDO: ubicacion_posicion incorrecta."
    print(f"DEBUG: Verificación post-instalación OK.")
    # ------------------------------------------------------

    # --- Fin Setup ---

    # --- 2. Ejecución: Llamar al endpoint /instalados ---
    print("Ejecución: Llamando GET /api/v1/neumaticos/instalados...") # Corregir print tambien si quieres

    # --- *** CORRECCIÓN DE URL *** ---
    url_instalados = f"{NEUMATICOS_PREFIX}/instalados"
    response = await integration_client.get(url_instalados, headers=headers)
     # --- *** FIN CORRECCIÓN *** ---

    print(f"Ejecución: Respuesta recibida - Status: {response.status_code}")

    # --- 3. Verificación ---
    assert response.status_code == status.HTTP_200_OK, f"GET /instalados (integration) failed: {response.text}"
    instalados_data = response.json()
    assert isinstance(instalados_data, list)
    print(f"Verificación: Recibidos {len(instalados_data)} neumáticos instalados.")

    # Buscar nuestro neumático específico en la respuesta
    neumatico_encontrado_data = None
    for item in instalados_data:
        if item.get("id") == str(neumatico_id):
            neumatico_encontrado_data = item
            break

    assert neumatico_encontrado_data is not None, f"Neumático {neumatico_id} no encontrado en la respuesta de /instalados."
    print(f"Verificación: Neumático {neumatico_id} encontrado en la respuesta.")

    # Verificar algunos campos clave devueltos por la vista
    assert neumatico_encontrado_data.get("numero_serie") == neumatico_a_instalar.numero_serie
    assert neumatico_encontrado_data.get("nombre_modelo") == modelo.nombre_modelo
    assert neumatico_encontrado_data.get("fabricante") == fabricante.nombre
    assert neumatico_encontrado_data.get("numero_economico") == vehiculo.numero_economico
    assert neumatico_encontrado_data.get("codigo_posicion") == posicion.codigo_posicion
    # ... (más aserciones sobre los datos de la vista si es necesario) ...
    print("Verificación: Campos básicos del neumático instalado coinciden.")

    print("--- Finalizando test_leer_neumaticos_instalados_success (Integración) OK ---")



@pytest.mark.asyncio
async def test_crear_evento_inspeccion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento INSPECCION."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)

    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": 8.5,
        "presion_psi": 105.0,
        "notas": "Inspección de rutina OK",
    }
    # --- CORRECCIÓN ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Insp failed: {response.text}"
    data = response.json()
    assert data["tipo_evento"] == TipoEventoNeumaticoEnum.INSPECCION.value
    assert data["profundidad_remanente_mm"] is not None and abs(Decimal(str(data["profundidad_remanente_mm"])) - Decimal("8.5")) < Decimal("0.01")
    assert data["presion_psi"] is not None and abs(Decimal(str(data["presion_psi"])) - Decimal("105.0")) < Decimal("0.01")

@pytest.mark.asyncio
async def test_crear_evento_rotacion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento ROTACION."""
    headers, neumatico_id, vehiculo_id, posicion1_id = await setup_instalacion_prerequisites(client, db_session)

    # --- CORRECCIÓN (URL para instalación dentro del test) ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    resp_inst = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion1_id),
        "odometro_vehiculo_en_evento": 20000
        }, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert resp_inst.status_code == status.HTTP_201_CREATED

    pos1_db = await db_session.get(PosicionNeumatico, posicion1_id)
    assert pos1_db is not None
    config_eje1 = await db_session.get(ConfiguracionEje, pos1_db.configuracion_eje_id)
    assert config_eje1 is not None

    codigo_pos2 = f"E{config_eje1.numero_eje}RD-T"
    stmt_pos2 = select(PosicionNeumatico).where(PosicionNeumatico.configuracion_eje_id == config_eje1.id, PosicionNeumatico.codigo_posicion == codigo_pos2)
    posicion_destino = (await db_session.exec(stmt_pos2)).first()
    if not posicion_destino:
        posicion_destino = PosicionNeumatico(
             configuracion_eje_id=config_eje1.id, codigo_posicion=codigo_pos2,
             lado=LadoVehiculoEnum.DERECHO, posicion_relativa=1,
             es_direccion=pos1_db.es_direccion
             )
        db_session.add(posicion_destino); await db_session.commit(); await db_session.refresh(posicion_destino)
    posicion_destino_id = posicion_destino.id

    odometro_rotacion = 25000
    evento_rotacion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.ROTACION.value,
        "vehiculo_id": str(vehiculo_id),
        "posicion_id": str(posicion_destino_id),
        "odometro_vehiculo_en_evento": odometro_rotacion,
        "notas": "Rotación de prueba"
    }
    # --- CORRECCIÓN (URL para rotación) ---
    # url_eventos ya definida arriba
    response = await client.post(url_eventos, json=evento_rotacion_payload, headers=headers) # <-- Usa url_eventos
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Rotation failed: {response.text}"

    neumatico_rotado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_rotado
    assert neumatico_rotado.ubicacion_actual_posicion_id == posicion_destino_id
    assert neumatico_rotado.ubicacion_actual_vehiculo_id == vehiculo_id


@pytest.mark.asyncio
async def test_crear_evento_reparacion_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_ENTRADA."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    almacen_taller = await get_or_create_almacen_test(db_session)

    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_ENTRADA.value,
        "proveedor_servicio_id": str(proveedor_reparacion.id),
        "almacen_destino_id": str(almacen_taller.id),
        "notas": "Entrada a reparación por pinchazo"
    }
    # --- CORRECCIÓN ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Ent failed: {response.text}"

    neumatico_en_rep = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_en_rep
    assert neumatico_en_rep.estado_actual == EstadoNeumaticoEnum.EN_REPARACION
    assert neumatico_en_rep.ubicacion_almacen_id == almacen_taller.id

@pytest.mark.asyncio
async def test_crear_evento_reparacion_salida_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_SALIDA."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    almacen_taller = await get_or_create_almacen_test(db_session)
    almacen_destino = await get_or_create_almacen_test(db_session)

    # --- CORRECCIÓN (URL para entrada a reparación dentro del test) ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    resp_entrada = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "REPARACION_ENTRADA",
        "proveedor_servicio_id": str(proveedor_reparacion.id),
        "almacen_destino_id": str(almacen_taller.id)
    }, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert resp_entrada.status_code == status.HTTP_201_CREATED

    neumatico_en_taller = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_en_taller and neumatico_en_taller.estado_actual == EstadoNeumaticoEnum.EN_REPARACION

    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_SALIDA.value,
        "proveedor_servicio_id": str(proveedor_reparacion.id),
        "costo_evento": 50.0,
        "almacen_destino_id": str(almacen_destino.id),
        "notas": "Reparación completada"
    }
    # --- CORRECCIÓN (URL para salida de reparación) ---
    # url_eventos ya definida arriba
    response = await client.post(url_eventos, json=evento_payload, headers=headers) # <-- Usa url_eventos
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Sal failed: {response.text}"

    neumatico_reparado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_reparado
    assert neumatico_reparado.estado_actual == EstadoNeumaticoEnum.EN_STOCK
    assert neumatico_reparado.ubicacion_almacen_id == almacen_destino.id

@pytest.mark.asyncio
async def test_crear_evento_reencauche_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REENCAUCHE_ENTRADA."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reencauche = await get_or_create_proveedor_reencauche(db_session)
    almacen_reencauchadora = await get_or_create_almacen_test(db_session)

    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA.value,
        "proveedor_servicio_id": str(proveedor_reencauche.id),
        "almacen_destino_id": str(almacen_reencauchadora.id),
        "notas": "Enviado a reencauche"
    }
    # --- CORRECCIÓN ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Reen Ent failed: {response.text}"

    neumatico_en_reenc = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_en_reenc
    assert neumatico_en_reenc.estado_actual == EstadoNeumaticoEnum.EN_REENCAUCHE
    assert neumatico_en_reenc.ubicacion_almacen_id == almacen_reencauchadora.id


# --- TEST REENCAUCHE_SALIDA RESTAURADO (ASUMIENDO REFACTORIZACIÓN) ---
@pytest.mark.asyncio
async def test_crear_evento_reencauche_salida_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REENCAUCHE_SALIDA (con lógica refactorizada en API/Servicio)."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reencauche = await get_or_create_proveedor_reencauche(db_session)
    almacen_reencauchadora = await get_or_create_almacen_test(db_session)
    almacen_destino = await get_or_create_almacen_test(db_session)

    # Forzar entrada a reencauche
    # --- CORRECCIÓN (URL para entrada a reencauche dentro del test) ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    resp_entrada = await client.post(url_eventos, json={ # <-- Usa url_eventos
        "neumatico_id": str(neumatico_id), "tipo_evento": "REENCAUCHE_ENTRADA",
        "proveedor_servicio_id": str(proveedor_reencauche.id),
        "almacen_destino_id": str(almacen_reencauchadora.id) # A dónde va para reencauchar
    }, headers=headers)
    assert resp_entrada.status_code == status.HTTP_201_CREATED
    await db_session.commit() # Asegurar que el estado EN_REENCAUCHE se guarde

    # Verificar pre-condición
    neumatico_antes_salida = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_antes_salida is not None
    assert neumatico_antes_salida.estado_actual == EstadoNeumaticoEnum.EN_REENCAUCHE, "Precondición fallida: Neumático no quedó en EN_REENCAUCHE"

    # Datos para la salida
    profundidad_nueva = 16.0
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA.value,
        "proveedor_servicio_id": str(proveedor_reencauche.id),
        "costo_evento": 300.0,
        "profundidad_post_reencauche_mm": profundidad_nueva, # Requerido por schema/API
        "almacen_destino_id": str(almacen_destino.id) # A dónde va después
    }

    # Llamada a la API que ahora tiene la lógica
    response = await client.post(url_eventos, json=evento_payload, headers=headers) # <-- Usa url_eventos

    assert response.status_code == status.HTTP_201_CREATED, f"Reen Sal failed: {response.text}"
    await db_session.commit() # Guardar cambios hechos por la API

    # Obtener el neumático después de la operación
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues is not None

    # --- *** ASERCIONES RESTAURADAS (AHORA DEBEN PASAR) *** ---
    print(f"\nDEBUG: Estado leído post-salida: {neumatico_despues.estado_actual}")
    print(f"DEBUG: Reencauches leídos post-salida: {neumatico_despues.reencauches_realizados}")
    print(f"DEBUG: Es Reencauchado leído post-salida: {neumatico_despues.es_reencauchado}")

    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.EN_STOCK, f"Estado esperado EN_STOCK, obtenido {neumatico_despues.estado_actual}"
    assert neumatico_despues.reencauches_realizados == 1, f"Se esperaba 1 reencauche, se obtuvo {neumatico_despues.reencauches_realizados}"
    assert neumatico_despues.es_reencauchado is True, "Indicador es_reencauchado debería ser True"
    assert neumatico_despues.vida_actual >= 2, f"Se esperaba vida_actual >= 2, se obtuvo {neumatico_despues.vida_actual}" # Asumiendo que setup_compra inicia en vida 1
    assert neumatico_despues.kilometraje_acumulado == 0, f"Kilometraje no se reseteó a 0, es {neumatico_despues.kilometraje_acumulado}"
    # Comparar con Decimal para precisión
    assert neumatico_despues.profundidad_inicial_mm is not None and abs(Decimal(str(neumatico_despues.profundidad_inicial_mm)) - Decimal(str(profundidad_nueva))) < Decimal("0.01"), f"Profundidad inicial esperada {profundidad_nueva}, obtenida {neumatico_despues.profundidad_inicial_mm}"
    assert neumatico_despues.ubicacion_almacen_id == almacen_destino.id, "Ubicación de almacén incorrecta"
    assert neumatico_despues.fecha_ultimo_evento is not None
    # ---------------------------------------------------------

# --- Fin Test Reencauche Salida Restaurado ---

@pytest.mark.asyncio
async def test_crear_evento_ajuste_inventario_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento AJUSTE_INVENTARIO."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    notas_ajuste = "Ajuste inventario test por conteo físico"
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO.value,
        "notas": notas_ajuste,
    }
    # --- CORRECCIÓN ---
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_payload, headers=headers)
    # --- FIN CORRECCIÓN ---
    assert response.status_code == status.HTTP_201_CREATED, f"Ajuste Inv failed: {response.text}"
    data = response.json()
    assert data["notas"] == notas_ajuste
    neumatico_ajustado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_ajustado




# --- Pruebas de Generación de Alertas (Corregidas v12 - Final) ---
@pytest.mark.asyncio
async def test_evento_inspeccion_genera_alerta_profundidad_baja(
    client: AsyncClient, db_session: AsyncSession
):
    """
    Verifica que INSPECCION con profundidad < umbral genera alerta PROFUNDIDAD_BAJA.
    """
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    modelo_id = neumatico.modelo_id
    umbral_minimo = 5.0
    param_db = await set_profundidad_minima_param(db_session, modelo_id, umbral_minimo)
    assert param_db is not None

    profundidad_medida = 4.0
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": profundidad_medida,
    }
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    # Permitir 201 (creada) o 409 (ya existía no gestionada)
    assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_409_CONFLICT], f"Insp Baja failed: {response.text}"
    await db_session.commit()

    stmt_alerta = select(Alerta).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    ).order_by(Alerta.timestamp_generacion.desc())
    resultado_alertas = await db_session.exec(stmt_alerta)
    alertas_generadas = resultado_alertas.all()

    assert len(alertas_generadas) >= 1, "No se generó alerta PROFUNDIDAD_BAJA"
    alerta_reciente = alertas_generadas[0]
    # --- CORRECCIÓN v12: Verificar estado_alerta ---
    assert alerta_reciente.estado_alerta != 'GESTIONADA', "La alerta generada ya está gestionada"
    # --- FIN CORRECCIÓN v12 ---
    assert alerta_reciente.parametro_id == param_db.id
    assert alerta_reciente.datos_contexto is not None
    assert "profundidad_medida_mm" in alerta_reciente.datos_contexto
    assert "umbral_minimo_mm" in alerta_reciente.datos_contexto
    assert abs(Decimal(str(alerta_reciente.datos_contexto.get("profundidad_medida_mm"))) - Decimal(str(profundidad_medida))) < Decimal("0.01")
    assert abs(Decimal(str(alerta_reciente.datos_contexto.get("umbral_minimo_mm"))) - Decimal(str(umbral_minimo))) < Decimal("0.01")






@pytest.mark.asyncio
async def test_evento_inspeccion_no_genera_alerta_profundidad_ok(
    client: AsyncClient, db_session: AsyncSession
):
    """Verifica que INSPECCION con profundidad >= umbral NO genera alerta."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id)
    assert neumatico is not None
    modelo_id = neumatico.modelo_id
    umbral_minimo = 5.0
    await set_profundidad_minima_param(db_session, modelo_id, umbral_minimo)

    # Contar alertas ANTES
    stmt_count_before = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    # --- Aplicando Corrección v15 ---
    count_before = await db_session.scalar(stmt_count_before) or 0
    # --- Fin Corrección ---

    # Registrar inspección con profundidad OK
    profundidad_medida = 6.0
    evento_inspeccion_payload = { # No necesita tipado Dict[str, Any] aquí
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": profundidad_medida,
        "presion_psi": 110.0, # Añadir otros campos obligatorios si los hay
        "notas": "Inspección OK"
    }
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp OK failed: {response.text}"
    # No es necesario db_session.commit() aquí si la sesión de test maneja commits/rollbacks

    # Contar alertas DESPUÉS
    stmt_count_after = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    # --- Aplicando Corrección v15 ---
    count_after = await db_session.scalar(stmt_count_after) or 0
    # --- Fin Corrección ---

    assert count_after == count_before, f"Se generó alerta inesperada ({count_after}) para profundidad OK ({profundidad_medida} >= {umbral_minimo})"


@pytest.mark.asyncio
async def test_evento_inspeccion_no_genera_alerta_sin_profundidad(
    client: AsyncClient, db_session: AsyncSession
):
    """Verifica que INSPECCION sin dato de profundidad NO genera alerta."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id)
    assert neumatico is not None
    modelo_id = neumatico.modelo_id
    await set_profundidad_minima_param(db_session, modelo_id, 5.0) # Establecer umbral aunque no se use

    # Contar alertas ANTES
    stmt_count_before = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    # --- Aplicando Corrección v15 ---
    count_before = await db_session.scalar(stmt_count_before) or 0
    # --- Fin Corrección ---

    # Registrar inspección SIN profundidad
    evento_inspeccion_payload = { # No necesita tipado Dict[str, Any] aquí
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "presion_psi": 110.0,
        # "profundidad_remanente_mm": None, # O simplemente no incluirlo si es opcional
        "notas": "Inspección sin medir profundidad"
    }
    url_eventos = f"{NEUMATICOS_PREFIX}/eventos"
    response = await client.post(url_eventos, json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp sin prof failed: {response.text}"
    # No es necesario db_session.commit() aquí si la sesión de test maneja commits/rollbacks

    # Contar alertas DESPUÉS (CORREGIDO: Calcular count_after, no count_before de nuevo)
    stmt_count_after = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    # --- Aplicando Corrección v15 ---
    count_after = await db_session.scalar(stmt_count_after) or 0
    # --- Fin Corrección ---

    assert count_after == count_before, f"Se generó alerta inesperada ({count_after}) para inspección sin profundidad"

# --- Fin Pruebas de Alertas Corregidas ---