# tests/test_neumaticos.py
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

# Security & Core
from core.security import get_password_hash # Necesario para el helper
from core.security import create_access_token, get_password_hash
# Helpers (Asume que existe tests/helpers.py)
from tests.helpers import create_user_and_get_token
# Security & Core
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
    response_token = await client.post("/auth/token", data=login_data)
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
    """Establece el parámetro PROFUNDIDAD_MINIMA para un modelo."""
    stmt = select(ParametroInventario).where(
        ParametroInventario.parametro_tipo == 'PROFUNDIDAD_MINIMA',
        ParametroInventario.modelo_id == modelo_id,
        ParametroInventario.ubicacion_almacen_id.is_(None) # Parámetro general para el modelo
    )
    result = await db_session.exec(stmt)
    parametro = result.first()
    if parametro:
        parametro.valor_numerico = umbral
        parametro.activo = True
    else:
        parametro = ParametroInventario(
            parametro_tipo='PROFUNDIDAD_MINIMA', modelo_id=modelo_id,
            valor_numerico=umbral, activo=True
            # creado_por se podría añadir si se pasa current_user
        )
    db_session.add(parametro); await db_session.commit(); await db_session.refresh(parametro)
    return parametro
# --- FIN Funciones Helper ---


# --- Inicio de los Tests ---
@pytest.mark.asyncio
async def test_crear_evento_compra_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento COMPRA."""
    headers, neumatico_id, proveedor_id = await setup_compra_prerequisites(client, db_session)
    # El setup ya crea el neumático, aquí registramos el evento asociado si es necesario
    # o verificamos el estado inicial. El evento COMPRA podría ser implícito en la creación.
    # Si necesitas registrar explícitamente el evento COMPRA:
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.COMPRA.value,
        "proveedor_servicio_id": str(proveedor_id), # Usar proveedor de compra
        "costo_evento": 500.00, # Costo del neumático
        "moneda_costo": "PEN",
        "notas": "Evento de compra de prueba registrado",
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
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
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Install failed: {response.text}"

    # Verificar estado final del neumático volviendo a obtenerlo (get es más seguro post-commit)
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.INSTALADO # La aserción original que fallaba
    # Verificar campos adicionales actualizados por la lógica de la API/trigger
    assert neumatico_despues.ubicacion_actual_vehiculo_id == vehiculo_id
    assert neumatico_despues.ubicacion_actual_posicion_id == posicion_id
    assert neumatico_despues.ubicacion_almacen_id is None
    assert neumatico_despues.kilometraje_acumulado == 0 # Verificar reseteo de KM
    assert neumatico_despues.fecha_ultimo_evento is not None # Verificar que se actualizó la fecha


@pytest.mark.asyncio
async def test_crear_evento_desmontaje_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento DESMONTAJE a EN_STOCK."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # Realizar la instalación primero
    response_install = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": 5000
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"

    # Verificar pre-condición (instalado)
    neumatico_instalado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_instalado is not None
    assert neumatico_instalado.estado_actual == EstadoNeumaticoEnum.INSTALADO

    # Preparar desmontaje a stock
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
        "almacen_destino_id": str(almacen_destino_id) # Requerido si destino no es DESECHADO
    }
    response = await client.post("/neumaticos/eventos", json=evento_desmontaje_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Status esperado 201 para DESMONTAJE, obtenido {response.status_code}: {response.text}"

    # Verificar estado final
    await db_session.refresh(neumatico_instalado) # Refrescar el mismo objeto
    neumatico_despues = neumatico_instalado
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == destino # Debe ser EN_STOCK
    assert neumatico_despues.ubicacion_actual_vehiculo_id is None
    assert neumatico_despues.ubicacion_actual_posicion_id is None
    assert neumatico_despues.ubicacion_almacen_id == almacen_destino_id # Debe estar en almacén
    assert neumatico_despues.fecha_ultimo_evento is not None
    # Verificar KM (opcional, depende de si la API o trigger lo calculan)
    # assert neumatico_despues.kilometraje_acumulado == (odometro_desmontaje - 5000)

@pytest.mark.asyncio
async def test_crear_evento_desecho_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento DESECHO desde EN_STOCK."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)

    # Crear motivo de desecho
    motivo_codigo = f"TEST_DSCH_{uuid.uuid4().hex[:6]}"
    motivo = MotivoDesecho(codigo=motivo_codigo, descripcion="Test Desecho")
    db_session.add(motivo); await db_session.commit(); await db_session.refresh(motivo)
    motivo_id = motivo.id

    # Verificar pre-condición (no instalado)
    neumatico_antes = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_antes and neumatico_antes.estado_actual != EstadoNeumaticoEnum.INSTALADO

    evento_desecho_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESECHO.value,
        "motivo_desecho_id_evento": str(motivo_id),
        "profundidad_remanente_mm": 2.0, # Profundidad final
    }
    response = await client.post("/neumaticos/eventos", json=evento_desecho_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Desecho failed: {response.text}"

    # Verificar estado final
    await db_session.refresh(neumatico_antes)
    neumatico_despues = neumatico_antes
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.DESECHADO
    assert neumatico_despues.motivo_desecho_id == motivo_id
    assert neumatico_despues.fecha_desecho is not None
    assert neumatico_despues.ubicacion_almacen_id is None # No debería estar en almacén

@pytest.mark.asyncio
async def test_crear_evento_desecho_fallido_si_instalado(client: AsyncClient, db_session: AsyncSession):
    """Prueba que DESECHO falla si el neumático está INSTALADO."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # Instalar el neumático
    response_install = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id)
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"

    # Crear motivo de desecho
    motivo = MotivoDesecho(codigo=f"TEST_DSCH_FAIL_{uuid.uuid4().hex[:6]}", descripcion="Test Desecho Fallido")
    db_session.add(motivo); await db_session.commit(); await db_session.refresh(motivo)
    motivo_id = motivo.id

    # Intentar desechar directamente
    evento_desecho_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESECHO.value,
        "motivo_desecho_id_evento": str(motivo_id),
    }
    response = await client.post("/neumaticos/eventos", json=evento_desecho_payload, headers=headers)
    assert response.status_code == status.HTTP_409_CONFLICT # Esperamos conflicto
    assert "No se puede desechar un neumático INSTALADO" in response.text # Verificar mensaje

@pytest.mark.asyncio
async def test_leer_historial_neumatico_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /{neumatico_id}/historial."""
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # Registrar algunos eventos
    resp1 = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id), "odometro_vehiculo_en_evento": 1000
    }, headers=headers)
    assert resp1.status_code == status.HTTP_201_CREATED
    evento1_id = resp1.json()["id"]

    resp2 = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSPECCION",
        "odometro_vehiculo_en_evento": 5000, "profundidad_remanente_mm": 17.0
    }, headers=headers)
    assert resp2.status_code == status.HTTP_201_CREATED
    evento2_id = resp2.json()["id"]

    # Solicitar historial
    response = await client.get(f"/neumaticos/{neumatico_id}/historial", headers=headers)
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

    # Instalar
    response_install = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id)
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"

    # Intentar desmontar sin destino
    evento_desmontaje_payload_incompleto: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESMONTAJE.value,
        # Falta destino_desmontaje
        "odometro_vehiculo_en_evento": 10000,
    }
    response = await client.post("/neumaticos/eventos", json=evento_desmontaje_payload_incompleto, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY # Esperamos error de validación
    assert "destino_desmontaje es requerido" in response.text

# --- Tests de lectura (adaptados o simplificados) ---



# --- Test de Integración para /instalados ---
# --- Test de Integración Corregido para /instalados ---
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
        integration_client, postgres_session, "inst_integ_v2" # Usar sufijo diferente si se corre seguido
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
    response_install = await integration_client.post("/neumaticos/eventos", json=evento_instalacion, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Setup fallido: No se pudo instalar neumático vía API. Response: {response_install.text}"
    # Commit para asegurar que la transacción (incluyendo triggers) se complete
    await postgres_session.commit()
    print("Setup: Neumático instalado (llamada API y commit realizados).")

    # --- *** VERIFICACIÓN DIRECTA EN BD POST-INSTALACIÓN *** ---
    # (Añadida para depurar el fallo anterior)
    print(f"DEBUG: Verificando estado de neumático {neumatico_id} en BD post-instalación...")
    # Volver a obtener el neumático para ver su estado final real
    neumatico_verificado_db = await postgres_session.get(Neumatico, neumatico_id)
    assert neumatico_verificado_db is not None, f"DEBUG FALLIDO: Neumático {neumatico_id} no encontrado en BD después de instalar."
    print(f"DEBUG: Estado actual leído de BD: {neumatico_verificado_db.estado_actual}")
    print(f"DEBUG: Ubicacion Almacen ID leído de BD: {neumatico_verificado_db.ubicacion_almacen_id}")
    print(f"DEBUG: Ubicacion Vehiculo ID leído de BD: {neumatico_verificado_db.ubicacion_actual_vehiculo_id}")
    print(f"DEBUG: Ubicacion Posicion ID leído de BD: {neumatico_verificado_db.ubicacion_actual_posicion_id}")
    # Verificar que el estado y ubicaciones son los esperados DESPUÉS de la instalación
    assert neumatico_verificado_db.estado_actual == EstadoNeumaticoEnum.INSTALADO, f"DEBUG FALLIDO: Neumático {neumatico_id} no quedó en estado INSTALADO después del evento."
    assert neumatico_verificado_db.ubicacion_almacen_id is None, f"DEBUG FALLIDO: Neumático {neumatico_id} aún tiene ubicacion_almacen_id después de instalar."
    assert neumatico_verificado_db.ubicacion_actual_vehiculo_id == vehiculo_id, "DEBUG FALLIDO: ubicacion_vehiculo incorrecta post-instalación."
    assert neumatico_verificado_db.ubicacion_actual_posicion_id == posicion_id, "DEBUG FALLIDO: ubicacion_posicion incorrecta post-instalación."
    print(f"DEBUG: Verificación post-instalación OK.")
    # ------------------------------------------------------

    # --- Fin Setup ---

    # --- 2. Ejecución: Llamar al endpoint /instalados ---
    print("Ejecución: Llamando GET /neumaticos/instalados...")
    response = await integration_client.get("/neumaticos/instalados", headers=headers)
    print(f"Ejecución: Respuesta recibida - Status: {response.status_code}")

    # --- 3. Verificación ---
    assert response.status_code == status.HTTP_200_OK, f"GET /instalados (integration) failed: {response.text}"
    instalados_data = response.json()
    assert isinstance(instalados_data, list)
    print(f"Verificación: Recibidos {len(instalados_data)} neumáticos instalados.")

    # Buscar nuestro neumático específico en la respuesta
    neumatico_encontrado_data = None
    for item in instalados_data:
        # Comparar por 'id' ya que la vista ahora lo incluye y el schema lo espera
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
# ... (Aquí van el resto de tus funciones de prueba originales de test_neumaticos.py) ...

@pytest.mark.asyncio
async def test_crear_evento_inspeccion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento INSPECCION."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session) # Puede estar en stock o instalado

    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": 8.5,
        "presion_psi": 105.0,
        "notas": "Inspección de rutina OK",
        # "odometro_vehiculo_en_evento": 55000 # Opcional si está instalado
    }
    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp failed: {response.text}"
    data = response.json()
    assert data["tipo_evento"] == TipoEventoNeumaticoEnum.INSPECCION.value
    # Convertir a Decimal para comparación segura si es necesario
    assert data["profundidad_remanente_mm"] is not None and abs(Decimal(str(data["profundidad_remanente_mm"])) - Decimal("8.5")) < Decimal("0.01")
    assert data["presion_psi"] is not None and abs(Decimal(str(data["presion_psi"])) - Decimal("105.0")) < Decimal("0.01")

@pytest.mark.asyncio
async def test_crear_evento_rotacion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento ROTACION."""
    # Instalar neumático en una posición
    headers, neumatico_id, vehiculo_id, posicion1_id = await setup_instalacion_prerequisites(client, db_session)
    resp_inst = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion1_id),
        "odometro_vehiculo_en_evento": 20000
        }, headers=headers)
    assert resp_inst.status_code == status.HTTP_201_CREATED

    # Crear una segunda posición en el mismo eje (si no existe)
    pos1_db = await db_session.get(PosicionNeumatico, posicion1_id)
    assert pos1_db is not None
    config_eje1 = await db_session.get(ConfiguracionEje, pos1_db.configuracion_eje_id)
    assert config_eje1 is not None

    codigo_pos2 = f"E{config_eje1.numero_eje}RD-T" # Suponiendo lado derecho
    stmt_pos2 = select(PosicionNeumatico).where(PosicionNeumatico.configuracion_eje_id == config_eje1.id, PosicionNeumatico.codigo_posicion == codigo_pos2)
    posicion_destino = (await db_session.exec(stmt_pos2)).first()
    if not posicion_destino:
        posicion_destino = PosicionNeumatico(
             configuracion_eje_id=config_eje1.id, codigo_posicion=codigo_pos2,
             lado=LadoVehiculoEnum.DERECHO, posicion_relativa=1, # Ajustar si es dual
             es_direccion=pos1_db.es_direccion # Asumir mismas características
             )
        db_session.add(posicion_destino); await db_session.commit(); await db_session.refresh(posicion_destino)
    posicion_destino_id = posicion_destino.id

    # Registrar evento de rotación
    odometro_rotacion = 25000
    evento_rotacion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.ROTACION.value,
        "vehiculo_id": str(vehiculo_id), # Mismo vehículo
        "posicion_id": str(posicion_destino_id), # Nueva posición
        "odometro_vehiculo_en_evento": odometro_rotacion,
        "notas": "Rotación de prueba"
    }
    response = await client.post("/neumaticos/eventos", json=evento_rotacion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rotation failed: {response.text}"

    # Verificar que la ubicación del neumático se actualizó
    neumatico_rotado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_rotado
    assert neumatico_rotado.ubicacion_actual_posicion_id == posicion_destino_id
    assert neumatico_rotado.ubicacion_actual_vehiculo_id == vehiculo_id # Sigue en el mismo vehículo

@pytest.mark.asyncio
async def test_crear_evento_reparacion_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_ENTRADA."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    almacen_taller = await get_or_create_almacen_test(db_session) # Usar un almacén como taller

    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_ENTRADA.value,
        "proveedor_servicio_id": str(proveedor_reparacion.id),
        "almacen_destino_id": str(almacen_taller.id), # Ubicación del taller
        "notas": "Entrada a reparación por pinchazo"
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Ent failed: {response.text}"

    # Verificar estado y ubicación
    neumatico_en_rep = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_en_rep
    assert neumatico_en_rep.estado_actual == EstadoNeumaticoEnum.EN_REPARACION
    assert neumatico_en_rep.ubicacion_almacen_id == almacen_taller.id

@pytest.mark.asyncio
async def test_crear_evento_reparacion_salida_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_SALIDA."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    almacen_taller = await get_or_create_almacen_test(db_session) # Taller
    almacen_destino = await get_or_create_almacen_test(db_session) # Destino final (puede ser el mismo)

    # Forzar entrada a reparación
    resp_entrada = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "REPARACION_ENTRADA",
        "proveedor_servicio_id": str(proveedor_reparacion.id),
        "almacen_destino_id": str(almacen_taller.id)
    }, headers=headers)
    assert resp_entrada.status_code == status.HTTP_201_CREATED

    # Verificar pre-condición
    neumatico_en_taller = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_en_taller and neumatico_en_taller.estado_actual == EstadoNeumaticoEnum.EN_REPARACION

    # Registrar salida
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_SALIDA.value,
        "proveedor_servicio_id": str(proveedor_reparacion.id), # Proveedor que hizo el trabajo
        "costo_evento": 50.0,
        "almacen_destino_id": str(almacen_destino.id), # A dónde va después de reparar
        "notas": "Reparación completada"
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Sal failed: {response.text}"

    # Verificar estado final
    neumatico_reparado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_reparado
    assert neumatico_reparado.estado_actual == EstadoNeumaticoEnum.EN_STOCK
    assert neumatico_reparado.ubicacion_almacen_id == almacen_destino.id

@pytest.mark.asyncio
async def test_crear_evento_reencauche_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REENCAUCHE_ENTRADA."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reencauche = await get_or_create_proveedor_reencauche(db_session)
    almacen_reencauchadora = await get_or_create_almacen_test(db_session) # Simular almacén de reenc.

    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA.value,
        "proveedor_servicio_id": str(proveedor_reencauche.id),
        "almacen_destino_id": str(almacen_reencauchadora.id), # Ubicación de la reencauchadora
        "notas": "Enviado a reencauche"
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Reen Ent failed: {response.text}"

    # Verificar estado y ubicación
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
    almacen_reencauchadora = await get_or_create_almacen_test(db_session) # Origen
    almacen_destino = await get_or_create_almacen_test(db_session) # Destino final (podría ser otro)

    # Forzar entrada a reencauche
    resp_entrada = await client.post("/neumaticos/eventos", json={
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
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
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
        # Podría incluir campos adicionales en datos_evento si es necesario
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Ajuste Inv failed: {response.text}"
    data = response.json()
    assert data["notas"] == notas_ajuste
    # Verificar que el estado del neumático no cambió (a menos que el ajuste lo implique)
    neumatico_ajustado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_ajustado # Verificar que existe
    # assert neumatico_ajustado.estado_actual == EstadoNeumaticoEnum.EN_STOCK # O el estado esperado


# --- Pruebas de Generación de Alertas ---
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
    assert param_db is not None # Asegurar que el parámetro se creó/actualizó

    profundidad_medida = 4.0 # Debajo del umbral
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": profundidad_medida,
    }
    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp Baja failed: {response.text}"
    await db_session.commit() # Commit para que alert_service pueda ver el evento

    # Verificar que la alerta se creó en la BD
    stmt_alerta = select(Alerta).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    ).order_by(Alerta.timestamp_generacion.desc()) # Ordenar por si hay varias
    resultado_alertas = await db_session.exec(stmt_alerta)
    alertas_generadas = resultado_alertas.all()

    assert len(alertas_generadas) >= 1, "No se generó alerta PROFUNDIDAD_BAJA"
    alerta_reciente = alertas_generadas[0] # La más reciente
    assert alerta_reciente.parametro_id == param_db.id
    assert alerta_reciente.datos_contexto is not None
    assert "profundidad_medida_mm" in alerta_reciente.datos_contexto
    assert "umbral_minimo_mm" in alerta_reciente.datos_contexto
    # Comparar valores numéricos de forma segura
    assert abs(Decimal(str(alerta_reciente.datos_contexto.get("profundidad_medida_mm"))) - Decimal(str(profundidad_medida))) < Decimal("0.01")
    assert abs(Decimal(str(alerta_reciente.datos_contexto.get("umbral_minimo_mm"))) - Decimal(str(umbral_minimo))) < Decimal("0.01")

@pytest.mark.asyncio
async def test_evento_inspeccion_no_genera_alerta_profundidad_ok(
    client: AsyncClient, db_session: AsyncSession
):
    """Verifica que INSPECCION con profundidad >= umbral NO genera alerta."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    modelo_id = neumatico.modelo_id
    umbral_minimo = 5.0
    await set_profundidad_minima_param(db_session, modelo_id, umbral_minimo)

    # Contar alertas ANTES del evento
    stmt_count_before = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    result_count_before = await db_session.exec(stmt_count_before)
    count_before = result_count_before.first() or 0 # <-- Cambiado aquí

    # Registrar inspección con profundidad OK
    profundidad_medida = 6.0 # Por encima o igual al umbral
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": profundidad_medida,
    }
    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp OK failed: {response.text}"
    await db_session.commit()

    # Contar alertas DESPUÉS del evento
    stmt_count_after = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    result_count_after = await db_session.exec(stmt_count_after)
    count_after = result_count_after.first() or 0 # <-- Cambiado aquí

    assert count_after == count_before, "Se generó alerta inesperada para profundidad OK"


@pytest.mark.asyncio
async def test_evento_inspeccion_no_genera_alerta_sin_profundidad(
    client: AsyncClient, db_session: AsyncSession
):
    """Verifica que INSPECCION sin dato de profundidad NO genera alerta."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    modelo_id = neumatico.modelo_id
    await set_profundidad_minima_param(db_session, modelo_id, 5.0) # Establecer un umbral

    # Contar alertas ANTES
    stmt_count_before = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    result_count_before = await db_session.exec(stmt_count_before)
    count_before = result_count_before.first() or 0 # <-- Cambiado aquí

    # Registrar inspección SIN profundidad
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "presion_psi": 110.0, # Solo presión
        "notas": "Inspección sin medir profundidad"
    }
    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp sin prof failed: {response.text}"
    await db_session.commit()

    # Contar alertas DESPUÉS
    stmt_count_after = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    result_count_after = await db_session.exec(stmt_count_after)
    count_after = result_count_after.first() or 0 # <-- Cambiado aquí

    assert count_after == count_before, "Se generó alerta inesperada para inspección sin profundidad"

# --- Fin del archivo tests/test_neumaticos.py ---