# tests/helpers.py
import uuid
from typing import Dict, Optional, Tuple, Union 
from datetime import datetime, timezone, date
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status
import pytest
import sqlalchemy # Necesario si usas Column con sqlalchemy.String

# --- Importaciones para Pylance y uso en helpers ---
from decimal import Decimal
from models.usuario import Usuario
from models.fabricante import FabricanteNeumatico
from models.modelo import ModeloNeumatico
from models.proveedor import Proveedor
from models.neumatico import Neumatico
from models.tipo_vehiculo import TipoVehiculo
from models.vehiculo import Vehiculo 
from models.configuracion_eje import ConfiguracionEje
from models.posicion_neumatico import PosicionNeumatico
from models.parametro_inventario import ParametroInventario
from models.almacen import Almacen
from models.motivo_desecho import MotivoDesecho # Añadido si se usa
from models.alerta import Alerta # Añadido si se usa

from schemas.common import (
    EstadoNeumaticoEnum, TipoEventoNeumaticoEnum, TipoProveedorEnum,
    TipoEjeEnum, LadoVehiculoEnum, TipoParametroEnum, TipoAlertaEnum
)
# --- Fin importaciones ---

from core.security import get_password_hash, verify_password
from core.config import settings

API_PREFIX = settings.API_V1_STR
AUTH_PREFIX = f"{API_PREFIX}/auth"
NEUMATICOS_PREFIX = f"{API_PREFIX}/neumaticos"

# --- Helper Genérico Corregido con Debugging y manejo de None ---


# --- Función Auxiliar Principal (si aún la necesitas directamente) ---
# --- Función Auxiliar Principal (si aún la necesitas directamente) ---
async def create_user_and_get_token(
    client: AsyncClient, db_session: AsyncSession, user_suffix: str = "", rol: str = "OPERADOR", activo: bool = True, es_superusuario: bool = False
) -> Tuple[str, Dict[str, str]]:
    """Crea un usuario, inicia sesión y devuelve ID y headers."""
    # Genera un nombre de usuario y email únicos para evitar colisiones en ejecuciones rápidas
    unique_part = uuid.uuid4().hex[:6]
    username = f"testuser_{user_suffix}_{unique_part}"
    email = f"{username}@example.com"
    password = "testpassword"

    user = await create_test_user(db_session, username, email, password, rol=rol, activo=activo, es_superusuario=es_superusuario)
    headers = await get_auth_headers(client, username, password)

    return str(user.id), headers
# --- Función Base para Crear Usuario ---
async def create_test_user(db_session: AsyncSession, username: str, email: str, password: str, rol: str = "OPERADOR", activo: bool = True, es_superusuario: bool = False) -> Usuario:
    """Crea y guarda un usuario de prueba con contraseña hasheada."""
    user_id_uuid = uuid.uuid4()
    user = Usuario(
        id=user_id_uuid,
        username=username,
        email=email,
        hashed_password=get_password_hash(password), # ¡Aplicar hash aquí!
        activo=activo,
        rol=rol, # Añadir rol
        es_superusuario=es_superusuario,
        creado_en=datetime.now(timezone.utc) # Asegurar campo de auditoría
    )
    db_session.add(user)
    try:
        await db_session.commit()
        await db_session.refresh(user)
    except Exception as e:
        await db_session.rollback() # Importante hacer rollback si falla el commit
        print(f"Error al crear usuario de prueba {username}: {e}") # Log para depuración
        # Puedes decidir si relanzar la excepción o manejarla de otra forma
        raise e
    return user

# --- Función Base para Obtener Headers ---
async def get_auth_headers(client: AsyncClient, username: str, password: str) -> Dict[str, str]:
    """Inicia sesión y devuelve los headers de autorización."""
    login_data = {"username": username, "password": password}
    # Asegúrate que la URL de login sea correcta según tu router de autenticación
    # CORRECCIÓN: Usar la URL correcta para el endpoint de token
    response = await client.post(f"{AUTH_PREFIX}/token", data=login_data)

    # Verifica si el login fue exitoso antes de continuar
    if response.status_code != status.HTTP_200_OK: # Usar status.HTTP_200_OK
        print(f"Fallo el login para {username}: {response.status_code} {response.text}")
        # Decide cómo manejar el fallo de login, ¿debería fallar la prueba?
        response.raise_for_status() # Esto hará que la prueba falle si el login no es 200 OK

    token_data = response.json()
    token = token_data.get("access_token") # Usar .get() para seguridad

    if not token:
        print(f"ERROR [helpers]: No se encontró 'access_token' en la respuesta del token para {username}. Respuesta: {token_data}")
        # Decide cómo manejar la falta de token, ¿debería fallar la prueba?
        raise ValueError(f"No se recibió access_token para el usuario {username}") # Fallar si no hay token

    headers = {"Authorization": f"Bearer {token}"}
    return headers







# --- Otros Helpers Específicos (Manejan Optional) ---
async def create_user_and_get_token_for_fabr_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> Tuple[str, Dict[str, str]]: # Cambiar a Tuple, ya que get_auth_headers falla si no hay token
     return await create_user_and_get_token(client, db_session, f"fabr_{user_suffix}", rol="ADMIN", es_superusuario=True)

async def create_user_and_get_token_for_prov_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> Tuple[str, Dict[str, str]]: # Cambiar a Tuple
     return await create_user_and_get_token(client, db_session, f"prov_{user_suffix}", rol="ADMIN", es_superusuario=True)

async def create_user_and_get_token_for_tipov_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> Tuple[str, Dict[str, str]]: # Cambiar a Tuple
     return await create_user_and_get_token(client, db_session, f"tipov_{user_suffix}", rol="ADMIN", es_superusuario=True)

async def create_user_and_get_token_for_veh_tests(
     client: AsyncClient, db_session: AsyncSession, user_suffix: str
) -> Tuple[str, Dict[str, str]]: # Cambiar a Tuple
     return await create_user_and_get_token(client, db_session, f"veh_{user_suffix}", es_superusuario=True) # Ajustar rol si es necesario


# --- Helpers de Setup (Ajustados para manejar None y devolver 5 elementos) ---
async def setup_compra_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID]:
    """Crea usuario, token, fabricante, modelo, proveedor y almacén base."""
    print("DEBUG [setup_compra]: Iniciando...")
    # Usar la función refactorizada
    user_id_str, headers = await create_user_and_get_token(client, db_session, f"compra_prereq_{uuid.uuid4().hex[:4]}")
    user_id = uuid.UUID(user_id_str)
    print(f"DEBUG [setup_compra]: Usuario {user_id} y token OK.")

    test_suffix = uuid.uuid4().hex[:4]
    fabricante = FabricanteNeumatico(nombre=f"Fab Compra {test_suffix}", codigo_abreviado=f"FC{test_suffix}", activo=True, creado_por=user_id)
    db_session.add(fabricante); await db_session.commit(); await db_session.refresh(fabricante)

    modelo = ModeloNeumatico(
        fabricante_id=fabricante.id, nombre_modelo=f"Mod Compra {test_suffix}", medida="295/80R22.5",
        profundidad_original_mm=Decimal("18.0"), permite_reencauche=True, reencauches_maximos=1, activo=True, creado_por=user_id
    )
    db_session.add(modelo); await db_session.commit(); await db_session.refresh(modelo)

    proveedor = Proveedor(nombre=f"Prov Compra {test_suffix}", tipo_proveedor=TipoProveedorEnum.DISTRIBUIDOR, activo=True, creado_por=user_id)
    db_session.add(proveedor); await db_session.commit(); await db_session.refresh(proveedor)
    print(f"DEBUG [setup_compra]: Dependencias Fabricante/Modelo/Proveedor OK.")

    almacen = await get_or_create_almacen_test(db_session)
    print(f"DEBUG [setup_compra]: Almacén obtenido/creado: {almacen.id}")

    return headers, modelo.id, proveedor.id, almacen.id, user_id


async def setup_instalacion_prerequisites(
    client: AsyncClient, db_session: AsyncSession
) -> Tuple[Dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID]:
    """Crea neumático EN_STOCK, vehículo, posición y devuelve IDs + headers + user_id."""
    print("DEBUG [setup_instalacion]: Iniciando...")
    headers, modelo_id, proveedor_id, almacen_id, user_id_creador = await setup_compra_prerequisites(client, db_session)
    print(f"DEBUG [setup_instalacion]: Prerequisitos de compra OK.")

    serie_unica = f"SERIE-INSTPRE-{uuid.uuid4().hex[:8]}"
    neum = Neumatico(
        numero_serie=serie_unica, modelo_id=modelo_id, fecha_compra=date.today(),
        costo_compra=Decimal("500.00"), proveedor_compra_id=proveedor_id,
        estado_actual=EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id=almacen_id,
        creado_por=user_id_creador
    )
    db_session.add(neum); await db_session.commit(); await db_session.refresh(neum)
    neumatico_id = neum.id
    print(f"DEBUG [setup_instalacion]: Neumático {neumatico_id} creado OK.")

    user_id_audit = user_id_creador 
    print(f"DEBUG [setup_instalacion]: Usuario {user_id_audit} para auditoría.")

    test_suffix = uuid.uuid4().hex[:4]
    tipo_vehiculo = TipoVehiculo(nombre=f"TipoV Install {test_suffix}", ejes_standard=2, categoria_principal="CAMIÓN", activo=True, creado_por=user_id_audit)
    db_session.add(tipo_vehiculo); await db_session.commit(); await db_session.refresh(tipo_vehiculo)

    vehiculo = Vehiculo(
        numero_economico=f"ECO-INSTPRE-{test_suffix}", tipo_vehiculo_id=tipo_vehiculo.id, activo=True, creado_por=user_id_audit
    )
    db_session.add(vehiculo); await db_session.commit(); await db_session.refresh(vehiculo)

    config_eje = ConfiguracionEje(
        tipo_vehiculo_id=tipo_vehiculo.id, numero_eje=1, nombre_eje="Delantero Install",
        tipo_eje=TipoEjeEnum.DIRECCION, numero_posiciones=2, neumaticos_por_posicion=1, 
        activo=True, # Asegurar que esté activo
        creado_por=user_id_audit
    )
    db_session.add(config_eje); await db_session.commit(); await db_session.refresh(config_eje)

    posicion = PosicionNeumatico(
        configuracion_eje_id=config_eje.id,
        codigo_posicion=f"E1P1-IP{test_suffix}"[:10], # Código más corto
        descripcion="Posición para pruebas",
        lado=LadoVehiculoEnum.IZQUIERDO.value, # Pasar el valor del Enum explícitamente
        posicion_relativa=1,
        es_direccion=True,
        activo=True, # Asegurar que esté activo
        creado_por=user_id_audit
    )
    db_session.add(posicion); await db_session.commit(); await db_session.refresh(posicion)
    print(f"DEBUG [setup_instalacion]: Vehículo {vehiculo.id} y Posición {posicion.id} creados.")

    neumatico_check = await db_session.get(Neumatico, neumatico_id)
    if not neumatico_check or neumatico_check.estado_actual != EstadoNeumaticoEnum.EN_STOCK:
         pytest.fail(f"Neumático {neumatico_id} no está en estado EN_STOCK antes de prueba de instalación.")

    return headers, neumatico_id, vehiculo.id, posicion.id, user_id_creador


# --- Helpers para obtener/crear entidades específicas ---
async def get_or_create_proveedor(session: AsyncSession, nombre: str, tipo: TipoProveedorEnum, user_id: Optional[uuid.UUID] = None) -> Proveedor:
    """Obtiene o crea un proveedor genérico."""
    stmt = select(Proveedor).where(Proveedor.nombre == nombre).limit(1)
    result = await session.exec(stmt)
    prov = result.first()
    if not prov:
        if not user_id:
            user_result = await session.exec(select(Usuario).limit(1))
            user = user_result.first()
            user_id = user.id if user else None
            if not user_id: print(f"WARN [helpers]: No se encontró usuario para 'creado_por' en get_or_create_proveedor({nombre}).")

        prov = Proveedor(
             nombre=nombre, tipo_proveedor=tipo, activo=True,
             creado_por=user_id, ruc=f"RUC-{nombre[:3].upper()}-{uuid.uuid4().hex[:6]}"[:20]
         )
        session.add(prov)
        await session.commit()
        await session.refresh(prov)
    return prov

async def get_or_create_proveedor_reparacion(session: AsyncSession, user_id: uuid.UUID) -> Proveedor:
    return await get_or_create_proveedor(session, "Taller Test Reparacion V5", TipoProveedorEnum.SERVICIO_REPARACION, user_id)

async def get_or_create_proveedor_reencauche(session: AsyncSession, user_id: uuid.UUID) -> Proveedor:
     return await get_or_create_proveedor(session, "Reencauchadora Test V5", TipoProveedorEnum.SERVICIO_REENCAUCHE, user_id)

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

         almacen = Almacen(codigo=codigo, nombre=nombre, activo=True, creado_por=creador_id)
         session.add(almacen)
         await session.commit()
         await session.refresh(almacen)
     return almacen

# Helper para parámetro de profundidad mínima (Revisado)
async def set_profundidad_minima_param(
    session: AsyncSession, modelo_id: uuid.UUID, umbral: float, user_id: uuid.UUID, almacen_id: Optional[uuid.UUID] = None
) -> ParametroInventario:
     """Crea o actualiza el parámetro de profundidad mínima para un modelo/almacén."""
     stmt = select(ParametroInventario).where(
         ParametroInventario.modelo_id == modelo_id,
         ParametroInventario.almacen_id == almacen_id, 
         ParametroInventario.tipo_parametro == TipoParametroEnum.PROFUNDIDAD_MINIMA
     )
     result = await session.exec(stmt)
     param = result.first()

     now = datetime.now(timezone.utc)
     if param:
         param.valor_numerico = Decimal(str(umbral)) 
         param.activo = True 
         param.actualizado_en = now
         param.actualizado_por = user_id
     else:
        param = ParametroInventario(
             modelo_id=modelo_id, almacen_id=almacen_id,
             tipo_parametro=TipoParametroEnum.PROFUNDIDAD_MINIMA,
             valor_numerico=Decimal(str(umbral)), 
             activo=True, creado_por=user_id, creado_en=now
        )
     session.add(param)
     await session.commit()
     await session.refresh(param)
     print(f"DEBUG [helpers]: Parámetro profundidad mínima establecido en {umbral} para modelo {modelo_id} (Almacén: {almacen_id})")
     return param

# ===== FIN DE tests/helpers.py =====