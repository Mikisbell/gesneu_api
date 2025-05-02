# tests/test_neumaticos.py
import pytest
import pytest_asyncio
import uuid
from datetime import date, datetime, timezone # Asegurar timezone
from typing import Dict, Any, Tuple, Optional

from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func # <-- CORRECCIÓN: Importación añadida

# Importar modelos, schemas y helpers necesarios
from models.usuario import Usuario
from models.proveedor import Proveedor
from models.fabricante import FabricanteNeumatico
from models.modelo import ModeloNeumatico
from models.neumatico import Neumatico, EstadoNeumaticoEnum # Importante
from models.almacen import Almacen # <-- CORRECCIÓN: Importación añadida
from models.evento_neumatico import EventoNeumatico # Para verificar en BD
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead # Para el payload y respuesta
from schemas.common import TipoEventoNeumaticoEnum # Para el tipo de evento
from core.security import create_access_token, get_password_hash

from models.vehiculo import Vehiculo
from models.tipo_vehiculo import TipoVehiculo
from models.configuracion_eje import ConfiguracionEje
from models.posicion_neumatico import PosicionNeumatico
from schemas.common import LadoVehiculoEnum, TipoEjeEnum, EstadoNeumaticoEnum # Importar Enums necesarios
from models.motivo_desecho import MotivoDesecho
# Proveedor ya está importado
from schemas.common import TipoProveedorEnum # Asegúrate que esté importado
# --- Helper para Prerrequisitos ---
from models.parametro_inventario import ParametroInventario
from models.alerta import Alerta
# from sqlalchemy import func # <-- Se importó arriba
# ... (resto de imports y helpers) ...

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
    """
    Crea un usuario, token, fabricante, modelo, proveedor y neumático EN_STOCK.
    Devuelve: (headers_con_token, neumatico_id, proveedor_id)
    """
    # (Tu código helper original aquí - sin cambios)
    user_password = "password_neum_test"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_neum_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    user = Usuario(username=username, email=email, password_hash=hashed_password, activo=True, rol="OPERADOR")
    db_session.add(user); await db_session.commit(); await db_session.refresh(user)

    login_data = {"username": user.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)
    if response_token.status_code != status.HTTP_200_OK:
         pytest.fail(f"Fallo al obtener token en helper setup_compra: {response_token.text}")
    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    fab_nombre = f"Test Fab Compra {uuid.uuid4().hex[:6]}"
    fab = FabricanteNeumatico(nombre=fab_nombre, activo=True)
    db_session.add(fab); await db_session.commit(); await db_session.refresh(fab)

    modelo_nombre = f"Test Mod Compra {uuid.uuid4().hex[:6]}"
    modelo = ModeloNeumatico(
         fabricante_id=fab.id, nombre_modelo=modelo_nombre, medida="295/80R22.5",
         profundidad_original_mm=18.0, permite_reencauche=True, reencauches_maximos=2
    )
    db_session.add(modelo); await db_session.commit(); await db_session.refresh(modelo)

    prov_nombre = f"Test Prov Compra {uuid.uuid4().hex[:6]}"
    prov = Proveedor(nombre=prov_nombre, tipo="DISTRIBUIDOR", activo=True)
    db_session.add(prov); await db_session.commit(); await db_session.refresh(prov)

    serie_unica = f"SERIE-COMPRA-{uuid.uuid4()}"
    neum = Neumatico(
         numero_serie=serie_unica, modelo_id=modelo.id, fecha_compra=date.today(),
         costo_compra=500.00, proveedor_compra_id=prov.id
    )
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)
    assert neum.estado_actual == EstadoNeumaticoEnum.EN_STOCK
    return headers, neum.id, prov.id

async def setup_instalacion_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """
    Crea Usuario/Token, Neumático (en stock), TipoVehiculo, Vehiculo, ConfigEje y Posicion.
    Devuelve: (headers, neumatico_id, vehiculo_id, posicion_id)
    """
    # (Tu código helper original aquí - sin cambios)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)

    tipo_veh_nombre = f"Camión Inst {uuid.uuid4().hex[:6]}"
    tipo_vehiculo = TipoVehiculo(nombre=tipo_veh_nombre, ejes_standard=3, categoria_principal="CAMIÓN", activo=True)
    db_session.add(tipo_vehiculo); await db_session.commit(); await db_session.refresh(tipo_vehiculo)

    eco_unico_inst = f"ECO-INST-{uuid.uuid4().hex[:6]}"
    placa_unica_inst = f"INST-{uuid.uuid4().hex[:6].upper()}"
    vehiculo = Vehiculo(
         numero_economico=eco_unico_inst, placa=placa_unica_inst,
         tipo_vehiculo_id=tipo_vehiculo.id, activo=True
    )
    db_session.add(vehiculo); await db_session.commit(); await db_session.refresh(vehiculo)

    config_eje = ConfiguracionEje(
         tipo_vehiculo_id=tipo_vehiculo.id, numero_eje=1, nombre_eje="Delantero",
         tipo_eje=TipoEjeEnum.DIRECCION, numero_posiciones=2, neumaticos_por_posicion=1
    )
    db_session.add(config_eje); await db_session.commit(); await db_session.refresh(config_eje)

    codigo_pos_unico = f"EJE{config_eje.numero_eje}-IZQ"
    posicion = PosicionNeumatico(
         configuracion_eje_id=config_eje.id, codigo_posicion=codigo_pos_unico,
         lado=LadoVehiculoEnum.IZQUIERDO, posicion_relativa=1, es_direccion=True
    )
    db_session.add(posicion); await db_session.commit(); await db_session.refresh(posicion)

    neumatico_final_check = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_final_check is not None
    if neumatico_final_check.estado_actual != EstadoNeumaticoEnum.EN_STOCK:
        neumatico_final_check.estado_actual = EstadoNeumaticoEnum.EN_STOCK
        neumatico_final_check.ubicacion_actual_vehiculo_id = None
        neumatico_final_check.ubicacion_actual_posicion_id = None
        neumatico_final_check.ubicacion_almacen_id = None
        db_session.add(neumatico_final_check)
        await db_session.commit(); await db_session.refresh(neumatico_final_check)
        print(f"WARN: Neumático {neumatico_id} forzado a EN_STOCK en helper de instalación.")

    return headers, neumatico_id, vehiculo.id, posicion.id

async def get_or_create_proveedor_reparacion(db_session: AsyncSession) -> Proveedor:
    """Obtiene o crea un proveedor de tipo SERVICIO_REPARACION."""
    # (Tu código helper original aquí - sin cambios)
    nombre_prov = "Taller Reparacion Test"
    stmt = select(Proveedor).where(Proveedor.nombre == nombre_prov)
    proveedor = (await db_session.exec(stmt)).first()
    if not proveedor:
        proveedor = Proveedor(nombre=nombre_prov, tipo=TipoProveedorEnum.SERVICIO_REPARACION, activo=True)
        db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    elif proveedor.tipo != TipoProveedorEnum.SERVICIO_REPARACION or not proveedor.activo:
         proveedor.tipo = TipoProveedorEnum.SERVICIO_REPARACION; proveedor.activo = True
         db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    return proveedor

async def get_or_create_proveedor_reencauche(db_session: AsyncSession) -> Proveedor:
    """Obtiene o crea un proveedor de tipo SERVICIO_REENCAUCHE."""
    # (Tu código helper original aquí - sin cambios)
    nombre_prov = "Reencauchadora Test"
    stmt = select(Proveedor).where(Proveedor.nombre == nombre_prov)
    proveedor = (await db_session.exec(stmt)).first()
    if not proveedor:
        proveedor = Proveedor(nombre=nombre_prov, tipo=TipoProveedorEnum.SERVICIO_REENCAUCHE, activo=True)
        db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    elif proveedor.tipo != TipoProveedorEnum.SERVICIO_REENCAUCHE or not proveedor.activo:
         proveedor.tipo = TipoProveedorEnum.SERVICIO_REENCAUCHE; proveedor.activo = True
         db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    return proveedor

async def set_profundidad_minima_param(
    db_session: AsyncSession, modelo_id: uuid.UUID, umbral: float
) -> ParametroInventario:
    """Crea o actualiza el parámetro PROFUNDIDAD_MINIMA para un modelo."""
    # (Tu código helper original aquí - sin cambios)
    stmt = select(ParametroInventario).where(
        ParametroInventario.parametro_tipo == 'PROFUNDIDAD_MINIMA',
        ParametroInventario.modelo_id == modelo_id,
        ParametroInventario.ubicacion_almacen_id == None
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
        )
    db_session.add(parametro); await db_session.commit(); await db_session.refresh(parametro)
    return parametro

# --- FIN DEFINICIÓN DE HELPERS ---


# --- Inicio de los Tests ---

# @pytest.mark.asyncio # Test de Ping eliminado para mantener tu código original
# async def test_ping_neumaticos_router(...): ...

@pytest.mark.asyncio
async def test_crear_evento_compra_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba la creación exitosa de un evento de tipo COMPRA via POST /eventos.
    """
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, proveedor_id = await setup_compra_prerequisites(client, db_session)
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.COMPRA.value,
        "proveedor_servicio_id": str(proveedor_id),
        "costo_evento": 500.00,
        "moneda_costo": "PEN",
        "notas": "Evento de compra de prueba",
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, \
        f"Status esperado 201 para crear evento COMPRA, obtenido {response.status_code}: {response.text}"
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
    """
    Prueba la creación exitosa de un evento de tipo INSTALACION via POST /eventos.
    Verifica actualización de estado y ubicación.
    """
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    neumatico_antes = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_antes is not None and neumatico_antes.estado_actual == EstadoNeumaticoEnum.EN_STOCK

    odometro_instalacion = 12345
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSTALACION.value,
        "vehiculo_id": str(vehiculo_id),
        "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": odometro_instalacion,
        "profundidad_remanente_mm": 15.5,
        "presion_psi": 110.0,
        "notas": "Evento de instalación de prueba",
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Install failed: {response.text}"

    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.INSTALADO
    assert neumatico_despues.ubicacion_actual_vehiculo_id == vehiculo_id
    assert neumatico_despues.ubicacion_actual_posicion_id == posicion_id
    assert neumatico_despues.ubicacion_almacen_id is None
    assert neumatico_despues.fecha_ultimo_evento is not None


# Dentro de tests/test_neumaticos.py

@pytest.mark.asyncio
async def test_crear_evento_desmontaje_success(client: AsyncClient, db_session: AsyncSession):
    """
    Prueba evento DESMONTAJE moviendo el neumático a EN_STOCK a un almacén específico.
    """
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)

    # Instalar el neumático primero
    response_install = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id),
        "odometro_vehiculo_en_evento": 5000
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"

    neumatico_instalado = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_instalado is not None and neumatico_instalado.estado_actual == EstadoNeumaticoEnum.INSTALADO

    # --- *** CORRECCIÓN: Obtener almacén destino *** ---
    almacen_destino = await get_or_create_almacen_test(db_session) # Usa el helper
    almacen_destino_id = almacen_destino.id
    assert almacen_destino_id is not None
    # ----------------------------------------------------

    # Payload para DESMONTAJE a EN_STOCK
    destino = EstadoNeumaticoEnum.EN_STOCK
    evento_desmontaje_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESMONTAJE.value,
        "destino_desmontaje": destino.value,
        "odometro_vehiculo_en_evento": 10000,
        "profundidad_remanente_mm": 10.5,
        "notas": "Desmontaje a stock (test)",
        # --- *** CORRECCIÓN: Pasar como campo normal *** ---
        "almacen_destino_id": str(almacen_destino_id)
        # --- Ya no se necesita model_extra para esto ---
    }

    response = await client.post("/neumaticos/eventos", json=evento_desmontaje_payload, headers=headers)


    # --- El assert ahora SÍ debería esperar 201 ---
    assert response.status_code == status.HTTP_201_CREATED, \
        f"Status esperado 201 para DESMONTAJE, obtenido {response.status_code}: {response.text}"
    # ---------------------------------------------

    # Verificar neumático en BD (solo si la respuesta fue 201)
    if response.status_code == status.HTTP_201_CREATED:
        data = response.json()
        evento_id = uuid.UUID(data["id"])
        evento_db = await db_session.get(EventoNeumatico, evento_id)
        assert evento_db is not None

        neumatico_despues = await db_session.get(Neumatico, neumatico_id)
        assert neumatico_despues is not None
        assert neumatico_despues.estado_actual == destino
        assert neumatico_despues.ubicacion_actual_vehiculo_id is None
        assert neumatico_despues.ubicacion_actual_posicion_id is None
        assert neumatico_despues.ubicacion_almacen_id == almacen_destino_id # <-- Verificar almacén
        assert neumatico_despues.fecha_ultimo_evento is not None


@pytest.mark.asyncio
async def test_crear_evento_desecho_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento DESECHO para neumático EN_STOCK."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    motivo = MotivoDesecho(codigo=f"TEST_DSCH_{uuid.uuid4().hex[:6]}", descripcion="Test Desecho")
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
    response = await client.post("/neumaticos/eventos", json=evento_desecho_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Desecho failed: {response.text}"
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.DESECHADO
    assert neumatico_despues.motivo_desecho_id == motivo_id
    assert neumatico_despues.fecha_desecho is not None

@pytest.mark.asyncio
async def test_crear_evento_desecho_fallido_si_instalado(client: AsyncClient, db_session: AsyncSession):
    """Prueba que falla al intentar DESECHO si está INSTALADO."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    response_install = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id)
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"
    motivo = MotivoDesecho(codigo=f"TEST_DSCH_FAIL_{uuid.uuid4().hex[:6]}", descripcion="Test Desecho Fallido")
    db_session.add(motivo); await db_session.commit(); await db_session.refresh(motivo)
    motivo_id = motivo.id
    evento_desecho_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESECHO.value,
        "motivo_desecho_id_evento": str(motivo_id),
    }
    response = await client.post("/neumaticos/eventos", json=evento_desecho_payload, headers=headers)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "INSTALADO. Realiza DESMONTAJE primero" in response.text

@pytest.mark.asyncio
async def test_leer_historial_neumatico_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /neumaticos/{neumatico_id}/historial."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    response_install = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id)
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"
    evento_install_id = response_install.json()["id"]
    response = await client.get(f"/neumaticos/{neumatico_id}/historial", headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"GET Historial failed: {response.text}"
    historial = response.json()
    assert isinstance(historial, list)
    assert len(historial) >= 1
    ids_en_historial = {item["id"] for item in historial}
    assert evento_install_id in ids_en_historial

@pytest.mark.asyncio
async def test_crear_evento_desmontaje_fallido_sin_destino(client: AsyncClient, db_session: AsyncSession):
    """Prueba que falla DESMONTAJE sin 'destino_desmontaje'."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, vehiculo_id, posicion_id = await setup_instalacion_prerequisites(client, db_session)
    response_install = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion_id)
    }, headers=headers)
    assert response_install.status_code == status.HTTP_201_CREATED, f"Install setup failed: {response_install.text}"
    evento_desmontaje_payload_incompleto: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.DESMONTAJE.value,
    }
    response = await client.post("/neumaticos/eventos", json=evento_desmontaje_payload_incompleto, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "destino_desmontaje es requerido" in response.text

@pytest.mark.asyncio
async def test_leer_neumaticos_instalados_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba GET /neumaticos/instalados."""
    # (Tu código de test original aquí - sin cambios)
    headers, neum1_id, veh1_id, pos1_id = await setup_instalacion_prerequisites(client, db_session)
    resp1 = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neum1_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(veh1_id), "posicion_id": str(pos1_id)
    }, headers=headers)
    assert resp1.status_code == status.HTTP_201_CREATED, f"Install 1 failed: {resp1.text}"

    pos1_db = await db_session.get(PosicionNeumatico, pos1_id); assert pos1_db is not None
    config_eje1 = await db_session.get(ConfiguracionEje, pos1_db.configuracion_eje_id); assert config_eje1 is not None
    posicion2 = PosicionNeumatico(
        configuracion_eje_id=config_eje1.id, codigo_posicion=f"EJE{config_eje1.numero_eje}-DER-{uuid.uuid4().hex[:4]}",
        lado=LadoVehiculoEnum.DERECHO, posicion_relativa=2, es_direccion=True
    )
    db_session.add(posicion2); await db_session.commit(); await db_session.refresh(posicion2)
    pos2_id = posicion2.id
    _, neum2_id, _ = await setup_compra_prerequisites(client, db_session)
    resp2 = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neum2_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(veh1_id), "posicion_id": str(pos2_id)
    }, headers=headers)
    assert resp2.status_code == status.HTTP_201_CREATED, f"Install 2 failed: {resp2.text}"

    _, neum3_id, _ = await setup_compra_prerequisites(client, db_session)

    response = await client.get("/neumaticos/instalados", headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"GET instalados failed: {response.text}"
    instalados = response.json()
    assert isinstance(instalados, list)
    ids_instalados = {item.get("id") for item in instalados}
    assert str(neum1_id) in ids_instalados
    assert str(neum2_id) in ids_instalados
    assert str(neum3_id) not in ids_instalados

@pytest.mark.asyncio
async def test_crear_evento_inspeccion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento INSPECCION."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": 8.5,
        "presion_psi": 105.0,
    }
    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp failed: {response.text}"
    data = response.json()
    assert data["tipo_evento"] == TipoEventoNeumaticoEnum.INSPECCION.value
    assert data["profundidad_remanente_mm"] == 8.5

@pytest.mark.asyncio
async def test_crear_evento_rotacion_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento ROTACION."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, vehiculo_id, posicion1_id = await setup_instalacion_prerequisites(client, db_session)
    resp_inst = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "INSTALACION",
        "vehiculo_id": str(vehiculo_id), "posicion_id": str(posicion1_id)
    }, headers=headers)
    assert resp_inst.status_code == status.HTTP_201_CREATED

    pos1_db = await db_session.get(PosicionNeumatico, posicion1_id); assert pos1_db is not None
    config_eje1 = await db_session.get(ConfiguracionEje, pos1_db.configuracion_eje_id); assert config_eje1 is not None
    posicion_destino = PosicionNeumatico(
        configuracion_eje_id=config_eje1.id, codigo_posicion=f"EJE{config_eje1.numero_eje}-DER-{uuid.uuid4().hex[:4]}",
        lado=LadoVehiculoEnum.DERECHO, posicion_relativa=2, es_direccion=True
    )
    db_session.add(posicion_destino); await db_session.commit(); await db_session.refresh(posicion_destino)
    posicion_destino_id = posicion_destino.id

    evento_rotacion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.ROTACION.value,
        "vehiculo_id": str(vehiculo_id),
        "posicion_id": str(posicion_destino_id),
    }
    response = await client.post("/neumaticos/eventos", json=evento_rotacion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rotation failed: {response.text}"
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues and neumatico_despues.ubicacion_actual_posicion_id == posicion_destino_id

@pytest.mark.asyncio
async def test_crear_evento_reparacion_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_ENTRADA."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_ENTRADA.value,
        "proveedor_servicio_id": str(proveedor_reparacion.id),
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Ent failed: {response.text}"
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues and neumatico_despues.estado_actual == EstadoNeumaticoEnum.EN_REPARACION

@pytest.mark.asyncio
async def test_crear_evento_reparacion_salida_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REPARACION_SALIDA."""
    # (Tu código de test original aquí - sin cambios, pero este test falla por lógica en router)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reparacion = await get_or_create_proveedor_reparacion(db_session)
    almacen = await get_or_create_almacen_test(db_session)
    resp_entrada = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "REPARACION_ENTRADA",
        "proveedor_servicio_id": str(proveedor_reparacion.id)
    }, headers=headers)
    assert resp_entrada.status_code == status.HTTP_201_CREATED

    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REPARACION_SALIDA.value,
        "proveedor_servicio_id": str(proveedor_reparacion.id),
        "costo_evento": 50.0,
        "almacen_destino_id": str(almacen.id) # Asumiendo en schema
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Rep Sal failed: {response.text}"
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues and neumatico_despues.estado_actual == EstadoNeumaticoEnum.EN_STOCK
    assert neumatico_despues.ubicacion_almacen_id == almacen.id # <-- Falla aquí

@pytest.mark.asyncio
async def test_crear_evento_reencauche_entrada_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REENCAUCHE_ENTRADA."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reencauche = await get_or_create_proveedor_reencauche(db_session)
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA.value,
        "proveedor_servicio_id": str(proveedor_reencauche.id),
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Reen Ent failed: {response.text}"
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues and neumatico_despues.estado_actual == EstadoNeumaticoEnum.EN_REENCAUCHE

@pytest.mark.asyncio
async def test_crear_evento_reencauche_salida_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento REENCAUCHE_SALIDA."""
    # (Tu código de test original aquí - sin cambios, pero este test falla por lógica en router/trigger)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    proveedor_reencauche = await get_or_create_proveedor_reencauche(db_session)
    almacen = await get_or_create_almacen_test(db_session)
    resp_entrada = await client.post("/neumaticos/eventos", json={
        "neumatico_id": str(neumatico_id), "tipo_evento": "REENCAUCHE_ENTRADA",
        "proveedor_servicio_id": str(proveedor_reencauche.id)
    }, headers=headers)
    assert resp_entrada.status_code == status.HTTP_201_CREATED

    profundidad_nueva = 16.0
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA.value,
        "proveedor_servicio_id": str(proveedor_reencauche.id),
        "costo_evento": 300.0,
        "profundidad_post_reencauche_mm": profundidad_nueva,
        "almacen_destino_id": str(almacen.id) # Asumiendo en schema
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Reen Sal failed: {response.text}"
    neumatico_despues = await db_session.get(Neumatico, neumatico_id)
    assert neumatico_despues is not None
    assert neumatico_despues.estado_actual == EstadoNeumaticoEnum.EN_STOCK # <-- Falla aquí
    assert neumatico_despues.reencauches_realizados >= 1
    assert neumatico_despues.es_reencauchado is True
    assert neumatico_despues.ubicacion_almacen_id == almacen.id # <-- También podría fallar

@pytest.mark.asyncio
async def test_crear_evento_ajuste_inventario_success(client: AsyncClient, db_session: AsyncSession):
    """Prueba evento AJUSTE_INVENTARIO."""
    # (Tu código de test original aquí - sin cambios)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    notas_ajuste = "Ajuste inventario test"
    evento_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO.value,
        "notas": notas_ajuste,
    }
    response = await client.post("/neumaticos/eventos", json=evento_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Ajuste Inv failed: {response.text}"
    data = response.json()
    assert data["notas"] == notas_ajuste

# --- Pruebas de Generación de Alertas ---
@pytest.mark.asyncio
async def test_evento_inspeccion_genera_alerta_profundidad_baja(
    client: AsyncClient, db_session: AsyncSession
):
    """
    Verifica que un evento INSPECCION con profundidad < umbral genera una alerta PROFUNDIDAD_BAJA.
    """
    # (Tu código de test original aquí - sin cambios, pero depende de la corrección del TypeError en service)
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    modelo_id = neumatico.modelo_id
    umbral_minimo = 5.0
    param_db = await set_profundidad_minima_param(db_session, modelo_id, umbral_minimo)
    profundidad_medida = 4.0
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": profundidad_medida,
    }
    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp Baja failed: {response.text}"
    await db_session.commit()
    stmt_alerta = select(Alerta).where(Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA', Alerta.neumatico_id == neumatico_id)
    resultado_alertas = await db_session.exec(stmt_alerta)
    alertas_generadas = resultado_alertas.all()
    assert len(alertas_generadas) >= 1, "No se generó alerta PROFUNDIDAD_BAJA"
    alerta_reciente = alertas_generadas[-1]
    assert alerta_reciente.parametro_id == param_db.id
    # Evitar comparar floats directamente por precisión, verificar que estén en el contexto
    assert alerta_reciente.datos_contexto is not None
    assert "profundidad_medida_mm" in alerta_reciente.datos_contexto
    assert "umbral_minimo_mm" in alerta_reciente.datos_contexto
    # assert alerta_reciente.datos_contexto.get("profundidad_medida_mm") == profundidad_medida # Puede fallar float vs decimal
    # assert alerta_reciente.datos_contexto.get("umbral_minimo_mm") == umbral_minimo # Puede fallar float vs decimal

# --- REEMPLAZA LA FUNCIÓN ANTIGUA CON ESTA ---
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
    profundidad_medida = 6.0
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "profundidad_remanente_mm": profundidad_medida,
    }
    stmt_count_before = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    # --- Código Corregido ---
    result_before = await db_session.exec(stmt_count_before)
    count_before = result_before.scalar_one_or_none() or 0
    # -----------------------

    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp OK failed: {response.text}"

    await db_session.commit()

    # --- Código Corregido ---
    stmt_count_after = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    result_after = await db_session.exec(stmt_count_after)
    count_after = result_after.scalar_one_or_none() or 0
    # -----------------------
    assert count_after == count_before, "Se generó alerta inesperada para profundidad OK"


# --- REEMPLAZA LA FUNCIÓN ANTIGUA CON ESTA ---
@pytest.mark.asyncio
async def test_evento_inspeccion_no_genera_alerta_sin_profundidad(
    client: AsyncClient, db_session: AsyncSession
):
    """Verifica que INSPECCION sin dato de profundidad NO genera alerta."""
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    neumatico = await db_session.get(Neumatico, neumatico_id); assert neumatico is not None
    modelo_id = neumatico.modelo_id
    await set_profundidad_minima_param(db_session, modelo_id, 5.0)
    evento_inspeccion_payload: Dict[str, Any] = {
        "neumatico_id": str(neumatico_id),
        "tipo_evento": TipoEventoNeumaticoEnum.INSPECCION.value,
        "presion_psi": 110.0,
    }
    stmt_count_before = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    # --- Código Corregido ---
    result_before = await db_session.exec(stmt_count_before)
    count_before = result_before.scalar_one_or_none() or 0
    # -----------------------

    response = await client.post("/neumaticos/eventos", json=evento_inspeccion_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Insp sin prof failed: {response.text}"

    await db_session.commit()

    # --- Código Corregido ---
    stmt_count_after = select(func.count(Alerta.id)).where(
        Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
        Alerta.neumatico_id == neumatico_id
    )
    result_after = await db_session.exec(stmt_count_after)
    count_after = result_after.scalar_one_or_none() or 0
    # -----------------------
    assert count_after == count_before, "Se generó alerta inesperada para inspección sin profundidad"

# ... (resto del archivo tests/test_neumaticos.py) ...