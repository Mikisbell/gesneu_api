# services/alert_service.py
import uuid
import logging
from decimal import Decimal # Importar Decimal
from typing import Dict, Any, Optional
from sqlmodel import select
from sqlalchemy.sql import func
from sqlmodel.ext.asyncio.session import AsyncSession

# Importar modelos y schemas necesarios
from models.neumatico import Neumatico
from models.evento_neumatico import EventoNeumatico
from models.parametro_inventario import ParametroInventario
from models.alerta import Alerta
from models.modelo import ModeloNeumatico
from models.almacen import Almacen
# Importar Enums desde la ubicación correcta
from schemas.common import EstadoNeumaticoEnum, TipoEventoNeumaticoEnum

logger = logging.getLogger(__name__)

# --- Función HELPER para convertir Decimal en el contexto ---
def _convert_context_for_json(context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convierte valores Decimal a float dentro de un diccionario para serialización JSON."""
    if context is None:
        return None
    new_context = {}
    for k, v in context.items():
        if isinstance(v, Decimal):
            new_context[k] = float(v) # Convertir a float
        # Podrías añadir aquí conversiones para otros tipos si es necesario
        else:
            new_context[k] = v
    return new_context
# ----------------------------------------------------------

async def crear_alerta_en_db(
    session: AsyncSession,
    tipo_alerta: str,
    mensaje: str,
    nivel_severidad: str,
    # --- Argumentos completos ---
    neumatico_id: Optional[uuid.UUID] = None,
    modelo_id: Optional[uuid.UUID] = None,
    almacen_id: Optional[uuid.UUID] = None,
    vehiculo_id: Optional[uuid.UUID] = None,
    parametro_id: Optional[uuid.UUID] = None,
    # ----------------------------
    datos_contexto: Optional[Dict[str, Any]] = None
):
    """
    Función helper para insertar una nueva alerta en la BD.
    Convierte datos_contexto para ser JSON serializable.
    """
    try:
        datos_contexto_serializable = _convert_context_for_json(datos_contexto)

        nueva_alerta = Alerta(
            tipo_alerta=tipo_alerta,
            mensaje=mensaje,
            nivel_severidad=nivel_severidad,
            estado_alerta='NUEVA', # Estado inicial
            # --- Usar los argumentos recibidos ---
            neumatico_id=neumatico_id,
            modelo_id=modelo_id,
            almacen_id=almacen_id,
            vehiculo_id=vehiculo_id,
            parametro_id=parametro_id,
            # --------------------------------------
            datos_contexto=datos_contexto_serializable # Contexto convertido
        )
        session.add(nueva_alerta)
        await session.commit()
        await session.refresh(nueva_alerta)
        logger.info(f"Alerta '{tipo_alerta}' creada con ID: {nueva_alerta.id}")
        return nueva_alerta
    except Exception as e:
        await session.rollback()
        logger.error(f"Error al crear alerta '{tipo_alerta}' en DB: {e}", exc_info=True)
        raise # Re-lanza la excepción


async def check_profundidad_baja(session: AsyncSession, evento: EventoNeumatico):
    """Verifica si la profundidad en un evento de inspección está bajo el umbral."""
    if evento.tipo_evento != TipoEventoNeumaticoEnum.INSPECCION or evento.profundidad_remanente_mm is None:
        return

    try:
        neumatico = await session.get(Neumatico, evento.neumatico_id)
        if not neumatico:
            logger.warning(f"Neumático {evento.neumatico_id} no encontrado en check_profundidad_baja.")
            return

        modelo_id = neumatico.modelo_id

        stmt_umbral = select(ParametroInventario).where(
            ParametroInventario.parametro_tipo == 'PROFUNDIDAD_MINIMA',
            ParametroInventario.modelo_id == modelo_id,
            ParametroInventario.activo == True
        ).order_by(ParametroInventario.ubicacion_almacen_id.desc().nulls_last())

        resultado_umbral = await session.exec(stmt_umbral)
        parametro = resultado_umbral.first()

        umbral_minimo = Decimal(str(parametro.valor_numerico)) if parametro and parametro.valor_numerico is not None else None
        profundidad_medida = Decimal(str(evento.profundidad_remanente_mm))

        if umbral_minimo is not None and profundidad_medida < umbral_minimo:
            mensaje = (
                f"Profundidad baja detectada para neumático {neumatico.id} "
                f"({profundidad_medida:.1f}mm < {umbral_minimo:.1f}mm)."
            )
            contexto = {
                "profundidad_medida_mm": profundidad_medida, # Pasa Decimal
                "umbral_minimo_mm": umbral_minimo,          # Pasa Decimal
                "modelo_id": str(modelo_id),
                "neumatico_id": str(neumatico.id),
                "evento_id": str(evento.id)
            }
            await crear_alerta_en_db(
                session=session,
                tipo_alerta='PROFUNDIDAD_BAJA',
                mensaje=mensaje,
                nivel_severidad='WARN',
                neumatico_id=neumatico.id,
                modelo_id=modelo_id,
                parametro_id=parametro.id if parametro else None,
                datos_contexto=contexto
            )
    except Exception as e:
        logger.error(f"Error en check_profundidad_baja para evento {evento.id}: {e}", exc_info=True)

# --- REEMPLAZA LA FUNCIÓN ANTIGUA CON ESTA ---
async def check_stock_minimo(session: AsyncSession, modelo_id: uuid.UUID, almacen_id: uuid.UUID):
    """Verifica si el stock de un modelo en un almacén está bajo el mínimo."""
    try:
        # 1. Obtener stock actual
        stmt_stock = select(func.count(Neumatico.id)).where(
            Neumatico.estado_actual == EstadoNeumaticoEnum.EN_STOCK,
            Neumatico.modelo_id == modelo_id,
            Neumatico.ubicacion_almacen_id == almacen_id
        )
        # --- Código Corregido ---
        result_stock = await session.exec(stmt_stock)             # Paso 1: Ejecutar
        stock_actual = result_stock.scalar_one_or_none() or 0     # Paso 2: Obtener escalar del resultado
        # -----------------------

        # 2. Obtener nivel mínimo
        stmt_param = select(ParametroInventario).where(
            ParametroInventario.parametro_tipo == 'NIVEL_MINIMO',
            ParametroInventario.modelo_id == modelo_id,
            ParametroInventario.activo == True
        ).order_by(ParametroInventario.ubicacion_almacen_id.desc().nulls_last())

        resultado_param_esp = await session.exec(stmt_param.where(ParametroInventario.ubicacion_almacen_id == almacen_id))
        parametro = resultado_param_esp.first()

        if not parametro:
             resultado_param_gen = await session.exec(stmt_param.where(ParametroInventario.ubicacion_almacen_id.is_(None)))
             parametro = resultado_param_gen.first()

        nivel_minimo = parametro.valor_numerico if parametro and parametro.valor_numerico is not None else None

        # 3. Comparar y crear alerta si es necesario
        if nivel_minimo is not None and stock_actual < nivel_minimo:
            modelo = await session.get(ModeloNeumatico, modelo_id)
            almacen = await session.get(Almacen, almacen_id)
            nombre_modelo = modelo.nombre_modelo if modelo else str(modelo_id)
            nombre_almacen = almacen.nombre if almacen else str(almacen_id)

            mensaje = (
                f"Stock bajo mínimo para {nombre_modelo} en {nombre_almacen} "
                f"({stock_actual} < {nivel_minimo:.0f})."
            )
            contexto = {
                "stock_actual": stock_actual,
                "nivel_minimo": nivel_minimo,
                "modelo_id": str(modelo_id),
                "almacen_id": str(almacen_id)
            }
            await crear_alerta_en_db(
                session=session,
                tipo_alerta='STOCK_MINIMO',
                mensaje=mensaje,
                nivel_severidad='WARN',
                modelo_id=modelo_id,
                almacen_id=almacen_id,
                parametro_id=parametro.id if parametro else None,
                datos_contexto=contexto
            )
    except Exception as e:
         logger.error(f"Error no crítico en check_stock_minimo para modelo {modelo_id}, almacén {almacen_id}: {e}", exc_info=True)
         # No relanzar el error aquí

# ... (resto del archivo services/alert_service.py) ...
