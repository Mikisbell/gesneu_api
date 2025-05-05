# tests/helpers.py (Versión Completa y Corregida - VERIFICADA)

import uuid
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone, date # <-- Imports datetime OK
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status
import pytest # <-- Import pytest OK

# --- Importar utilidades de seguridad ---
from core.security import get_password_hash, verify_password # OK

# --- Importar todos los Modelos y Enums necesarios para los helpers ---
from models.usuario import Usuario # OK
from models.fabricante import FabricanteNeumatico # OK
from models.modelo import ModeloNeumatico # OK
from models.proveedor import Proveedor # OK
# Importar Enums desde common es mejor práctica
from schemas.common import ( # OK (Importado desde common)
    TipoProveedorEnum, EstadoNeumaticoEnum, TipoEjeEnum,
    LadoVehiculoEnum, TipoParametroEnum
)
from models.tipo_vehiculo import TipoVehiculo # OK
from models.configuracion_eje import ConfiguracionEje # OK
from models.posicion_neumatico import PosicionNeumatico # OK
from models.vehiculo import Vehiculo # OK
from models.neumatico import Neumatico # OK
from models.almacen import Almacen # OK
from models.motivo_desecho import MotivoDesecho # OK
from models.parametro_inventario import ParametroInventario # OK

# --- Importar settings para obtener el prefijo de la API ---
from core.config import settings # OK

API_PREFIX = settings.API_V1_STR # Obtener el prefijo (ej: /api/v1) OK

# --- Helper Genérico Corregido ---
async def create_user_and_get_token(
    client: AsyncClient,
    session: AsyncSession,
    user_suffix: str,
    rol: str = "OPERADOR",
    activo: bool = True
) -> tuple[str, dict]:
    """
    Crea un usuario único para pruebas y devuelve su ID y headers con token.
    Funciona con cualquier sesión asíncrona. CORREGIDO para usar API_PREFIX.
    """
    user_password = f"password_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_{user_suffix}_{uuid.uuid4().hex[:4]}"
    email = f"{username}@example.com"

    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user_result = await session.exec(stmt_user)
    existing_user = existing_user_result.first()

    user: Usuario
    # Intentar asignar user_id dentro del if/else para asegurar que siempre tenga valor
    user_id: Optional[str] = None
    if not existing_user:
        user = Usuario(
            username=username, email=email, password_hash=hashed_password,
            activo=activo, rol=rol, creado_en=datetime.now(timezone.utc)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = str(user.id)
    else:
        # Si existiera, actualizar datos y obtener ID
        if not verify_password(user_password, existing_user.password_hash or ""):
             existing_user.password_hash = hashed_password
        existing_user.activo = activo
        existing_user.rol = rol
        existing_user.actualizado_en = datetime.now(timezone.utc)
        session.add(existing_user)
        await session.commit()
        await session.refresh(existing_user)
        user_id = str(existing_user.id)
        user = existing_user

    # Asegurarse que user_id se asignó
    if user_id is None:
        pytest.fail(f"No se pudo obtener/crear user_id para {username}")

    # Obtener token usando la ruta CORRECTA con prefijo
    login_data = {"username": user.username, "password": user_password}
    # ===========================
    # ===== RUTA CORREGIDA =====
    token_url = f"{API_PREFIX}/auth/token" # Usar el prefijo
    # ===========================
    print(f"DEBUG [helpers]: Solicitando token a: {token_url}")
    response_token = await client.post(token_url, data=login_data)

    if response_token.status_code != status.HTTP_200_OK:
        pytest.fail(
            f"Fallo al obtener token en helper genérico para user {user.username}: "
            f"{response_token.status_code} {response_token.text}. URL: {token_url}"
        )

    token_data = response_token.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"DEBUG [helpers]: Token obtenido para {user.username}")
    # Asegúrate de que user_id no sea None antes de devolverlo
    return user_id, headers

# --- Otros Helpers Específicos (Llaman al genérico corregido) ---
async def create_user_and_get_token_for_fabr_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
     return await create_user_and_get_token(client, db_session, f"fabr_{user_suffix}", rol="ADMIN")

async def create_user_and_get_token_for_prov_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
     return await create_user_and_get_token(client, db_session, f"prov_{user_suffix}", rol="ADMIN")

async def create_user_and_get_token_for_tipov_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
     return await create_user_and_get_token(client, db_session, f"tipov_{user_suffix}", rol="ADMIN")

async def create_user_and_get_token_for_veh_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> tuple[str, dict]:
     return await create_user_and_get_token(client, db_session, f"veh_{user_suffix}")


# --- Helpers de Setup (Centralizados aquí) ---
async def setup_compra_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID]:
    """Crea neumático base y dependencias (usuario, token, fab, mod, prov). CORREGIDO"""
    print("DEBUG [setup_compra]: Iniciando...")
    user_id_str, headers = await create_user_and_get_token(client, db_session, f"neum_compra_{uuid.uuid4().hex[:4]}")
    user_id = uuid.UUID(user_id_str)
    print(f"DEBUG [setup_compra]: Usuario {user_id} y token OK.")

    test_suffix = uuid.uuid4().hex[:4]
    fabricante = FabricanteNeumatico(nombre=f"Fab Compra {test_suffix}", codigo_abreviado=f"FC{test_suffix}", activo=True, creado_por=user_id)
    db_session.add(fabricante); await db_session.commit(); await db_session.refresh(fabricante)

    modelo = ModeloNeumatico(
        fabricante_id=fabricante.id, nombre_modelo=f"Mod Compra {test_suffix}", medida="295/80R22.5",
        profundidad_original_mm=18.0, permite_reencauche=True, reencauches_maximos=1, creado_por=user_id
    )
    db_session.add(modelo); await db_session.commit(); await db_session.refresh(modelo)

    proveedor = Proveedor(nombre=f"Prov Compra {test_suffix}", tipo_proveedor=TipoProveedorEnum.DISTRIBUIDOR, activo=True, creado_por=user_id)
    db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    print(f"DEBUG [setup_compra]: Dependencias Fabricante/Modelo/Proveedor OK.")

    neumatico = Neumatico(
        numero_serie=f"SERIE-COMPRA-{test_suffix}", modelo_id=modelo.id,
        fecha_compra=date.today(), costo_compra=750.0, proveedor_compra_id=proveedor.id,
        estado_actual=EstadoNeumaticoEnum.EN_STOCK,
        creado_por=user_id
    )
    db_session.add(neumatico); await db_session.commit(); await db_session.refresh(neumatico)
    print(f"DEBUG [setup_compra]: Neumático {neumatico.id} creado OK.")

    return headers, neumatico.id, proveedor.id

async def setup_instalacion_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Crea todo lo necesario para probar una instalación. CORREGIDO"""
    print("DEBUG [setup_instalacion]: Iniciando...")
    headers, neumatico_id, _ = await setup_compra_prerequisites(client, db_session)
    print(f"DEBUG [setup_instalacion]: Prerequisitos de compra OK (Neumático: {neumatico_id}).")

    user_id_str_audit, _ = await create_user_and_get_token(client, db_session, "install_audit_user")
    user_id_audit=uuid.UUID(user_id_str_audit)
    print(f"DEBUG [setup_instalacion]: Usuario {user_id_audit} para auditoría obtenido.")

    test_suffix = uuid.uuid4().hex[:4]
    tipo_vehiculo = TipoVehiculo(nombre=f"TipoV Install {test_suffix}", ejes_standard=2, categoria_principal="CAMIÓN", activo=True, creado_por=user_id_audit)
    db_session.add(tipo_vehiculo); await db_session.commit(); await db_session.refresh(tipo_vehiculo)

    vehiculo = Vehiculo(
        numero_economico=f"ECO-INST-{test_suffix}", tipo_vehiculo_id=tipo_vehiculo.id, activo=True, creado_por=user_id_audit
    )
    db_session.add(vehiculo); await db_session.commit(); await db_session.refresh(vehiculo)

    config_eje = ConfiguracionEje(
        tipo_vehiculo_id=tipo_vehiculo.id, numero_eje=1, nombre_eje="Delantero Install",
        tipo_eje=TipoEjeEnum.DIRECCION, numero_posiciones=2, neumaticos_por_posicion=1,
        creado_por=user_id_audit # Asumiendo que este modelo tiene auditoría
    )
    db_session.add(config_eje); await db_session.commit(); await db_session.refresh(config_eje)

    posicion = PosicionNeumatico(
        configuracion_eje_id=config_eje.id,
        codigo_posicion=f"1LI-I{test_suffix}"[:10],
        lado=LadoVehiculoEnum.IZQUIERDO,
        posicion_relativa=1,
        es_direccion=True,
        # creado_por=user_id_audit # Añadir si este modelo tiene auditoría
    )
    db_session.add(posicion); await db_session.commit(); await db_session.refresh(posicion)
    print(f"DEBUG [setup_instalacion]: Vehículo {vehiculo.id} y Posición {posicion.id} creados.")

    neumatico = await db_session.get(Neumatico, neumatico_id)
    if not neumatico or neumatico.estado_actual != EstadoNeumaticoEnum.EN_STOCK:
         pytest.fail(f"Neumático {neumatico_id} no está en estado EN_STOCK antes de prueba de instalación.")

    return headers, neumatico_id, vehiculo.id, posicion.id

# --- Helpers para obtener/crear entidades específicas ---
async def get_or_create_proveedor(session: AsyncSession, nombre: str, tipo: TipoProveedorEnum, user_id: Optional[uuid.UUID] = None) -> Proveedor:
    """Obtiene o crea un proveedor genérico."""
    stmt = select(Proveedor).where(Proveedor.nombre == nombre).limit(1)
    result = await session.exec(stmt)
    prov = result.first()
    if not prov:
        # Intentar obtener un user_id si no se proporcionó
        if not user_id:
            user_result = await session.exec(select(Usuario).limit(1))
            user = user_result.first()
            user_id = user.id if user else None
            if not user_id: print(f"WARN [helpers]: No se encontró usuario para 'creado_por' en get_or_create_proveedor({nombre}).")

        prov = Proveedor(
             nombre=nombre,
             tipo_proveedor=tipo,
             activo=True,
             creado_por=user_id
         )
        session.add(prov)
        await session.commit()
        await session.refresh(prov)
    return prov

async def get_or_create_proveedor_reparacion(session: AsyncSession) -> Proveedor:
    return await get_or_create_proveedor(session, "Taller Test Reparacion", TipoProveedorEnum.SERVICIO_REPARACION)

async def get_or_create_proveedor_reencauche(session: AsyncSession) -> Proveedor:
     return await get_or_create_proveedor(session, "Reencauchadora Test", TipoProveedorEnum.SERVICIO_REENCAUCHE)

async def get_or_create_almacen_test(session: AsyncSession, nombre: str = "Almacen Test Default") -> Almacen:
     codigo = f"ALM-{nombre.replace(' ','-').upper()[:6]}-{uuid.uuid4().hex[:4]}"[:20]
     stmt = select(Almacen).where(Almacen.nombre == nombre).limit(1)
     result = await session.exec(stmt)
     almacen = result.first()
     if not almacen:
         user_result = await session.exec(select(Usuario).limit(1))
         user = user_result.first()
         creador_id = user.id if user else None
         if not creador_id: print("WARN [helpers]: No se encontró usuario para 'creado_por' en get_or_create_almacen_test.")

         almacen = Almacen(
             codigo=codigo,
             nombre=nombre,
             activo=True,
             creado_por=creador_id
         )
         session.add(almacen)
         await session.commit()
         await session.refresh(almacen)
     return almacen

# Helper para parámetro de profundidad mínima (Usa TipoParametroEnum desde common)
async def set_profundidad_minima_param(
    session: AsyncSession, modelo_id: uuid.UUID, umbral: float, almacen_id: Optional[uuid.UUID] = None
) -> ParametroInventario:
     """Crea o actualiza el parámetro de profundidad mínima para un modelo/almacén."""
     stmt = select(ParametroInventario).where(
         ParametroInventario.modelo_id == modelo_id,
         ParametroInventario.almacen_id == almacen_id,
         ParametroInventario.tipo_parametro == TipoParametroEnum.PROFUNDIDAD_MINIMA
     )
     result = await session.exec(stmt)
     param = result.first()

     user_result = await session.exec(select(Usuario).limit(1))
     user = user_result.first()
     auditor_id = user.id if user else None
     if not auditor_id: print("WARN [helpers]: No se encontró usuario para auditoría en set_profundidad_minima_param.")

     now = datetime.now(timezone.utc)
     if param:
         param.valor_numerico = umbral
         param.actualizado_en = now
         param.actualizado_por = auditor_id
     else:
        param = ParametroInventario(
             modelo_id=modelo_id,
             almacen_id=almacen_id,
             tipo_parametro=TipoParametroEnum.PROFUNDIDAD_MINIMA,
             valor_numerico=umbral,
             activo=True,
             creado_por=auditor_id,
             creado_en=now
        )
     session.add(param)
     await session.commit()
     await session.refresh(param)
     print(f"DEBUG [helpers]: Parámetro profundidad mínima establecido en {umbral} para modelo {modelo_id} (Almacén: {almacen_id})")
     return param

# ===== FIN DE tests/helpers.py =====