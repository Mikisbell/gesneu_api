# services/alert_service.py
import uuid
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from sqlmodel import select
from sqlalchemy.sql import func
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone

# Importar modelos y schemas necesarios
from models.neumatico import Neumatico
from models.evento_neumatico import EventoNeumatico
from models.parametro_inventario import ParametroInventario
from models.alerta import Alerta
from models.modelo import ModeloNeumatico
from models.almacen import Almacen
# Importar Enums desde la ubicación correcta
from schemas.common import EstadoNeumaticoEnum, TipoEventoNeumaticoEnum, TipoParametroEnum

logger = logging.getLogger(__name__)

# --- Función HELPER para convertir Decimal en el contexto ---
def _convert_context_for_json(context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convierte valores Decimal a float dentro de un diccionario para serialización JSON."""
    if context is None:
        return None
    new_context = {}
    for k, v in context.items():
        if isinstance(v, Decimal):
            new_context[k] = float(v)
        else:
            new_context[k] = v
    return new_context
# ----------------------------------------------------------

async def crear_alerta_en_db(
    session: AsyncSession,
    tipo_alerta: str,
    mensaje: str,
    nivel_severidad: str,
    neumatico_id: Optional[uuid.UUID] = None,
    modelo_id: Optional[uuid.UUID] = None,
    almacen_id: Optional[uuid.UUID] = None,
    vehiculo_id: Optional[uuid.UUID] = None,
    parametro_id: Optional[uuid.UUID] = None,
    datos_contexto: Optional[Dict[str, Any]] = None
):
    """
    Función helper para insertar una nueva alerta en la BD.
    Verifica si ya existe una alerta similar no gestionada.
    """
    try:
        datos_contexto_serializable = _convert_context_for_json(datos_contexto)

        # --- CORRECCIÓN v5: Usar estado_alerta ---
        stmt_existente = select(Alerta).where(
            Alerta.tipo_alerta == tipo_alerta,
            Alerta.estado_alerta != 'GESTIONADA', # <-- Usar estado_alerta
            Alerta.neumatico_id == neumatico_id,
            Alerta.modelo_id == modelo_id,
            Alerta.almacen_id == almacen_id,
            Alerta.vehiculo_id == vehiculo_id
        )
        # --- FIN CORRECCIÓN v5 ---
        result_existente = await session.exec(stmt_existente)
        alerta_existente = result_existente.first()

        if alerta_existente:
            logger.info(f"Alerta '{tipo_alerta}' similar (ID: {alerta_existente.id}) ya existe y no está gestionada. No se crea una nueva.")
            return alerta_existente

        nueva_alerta = Alerta(
            tipo_alerta=tipo_alerta,
            mensaje=mensaje,
            nivel_severidad=nivel_severidad,
            estado_alerta='NUEVA',
            neumatico_id=neumatico_id,
            modelo_id=modelo_id,
            almacen_id=almacen_id,
            vehiculo_id=vehiculo_id,
            parametro_id=parametro_id,
            datos_contexto=datos_contexto_serializable
        )
        session.add(nueva_alerta)
        await session.commit()
        await session.refresh(nueva_alerta)
        logger.info(f"Alerta '{tipo_alerta}' creada con ID: {nueva_alerta.id}")
        return nueva_alerta
    except Exception as e:
        await session.rollback()
        logger.error(f"Error al crear/verificar alerta '{tipo_alerta}' en DB: {e}", exc_info=True)
        return None


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

        # --- CORRECCIÓN EN LA CONSULTA (v5 - Usar Enum) ---
        stmt_umbral = select(ParametroInventario).where(
            ParametroInventario.tipo_parametro == TipoParametroEnum.PROFUNDIDAD_MINIMA, # <-- Usar Enum
            ParametroInventario.modelo_id == modelo_id,
            ParametroInventario.activo == True,
            (ParametroInventario.almacen_id == neumatico.ubicacion_almacen_id) | (ParametroInventario.almacen_id.is_(None))
        ).order_by(
            ParametroInventario.almacen_id.desc().nulls_last()
        )
        # --- FIN CORRECCIÓN EN LA CONSULTA (v5) ---

        resultado_umbral = await session.exec(stmt_umbral)
        parametro = resultado_umbral.first()

        if not parametro or parametro.valor_numerico is None:
            logger.debug(f"No se encontró umbral de profundidad mínima activo para modelo {modelo_id}.")
            return

        umbral_minimo = Decimal(str(parametro.valor_numerico))
        profundidad_medida = Decimal(str(evento.profundidad_remanente_mm))

        if profundidad_medida < umbral_minimo:
            mensaje = (
                f"Profundidad baja detectada para neumático {neumatico.id} "
                f"({profundidad_medida:.1f}mm < {umbral_minimo:.1f}mm)."
            )
            contexto = {
                "profundidad_medida_mm": profundidad_medida,
                "umbral_minimo_mm": umbral_minimo,
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
                parametro_id=parametro.id,
                datos_contexto=contexto
            )
        else:
             # --- CORRECCIÓN v5: Usar estado_alerta ---
             stmt_resolver = select(Alerta).where(
                 Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
                 Alerta.neumatico_id == neumatico.id,
                 Alerta.estado_alerta != 'GESTIONADA' # <-- Usar estado_alerta
             )
             # --- FIN CORRECCIÓN v5 ---
             res_resolver = await session.exec(stmt_resolver)
             alertas_a_resolver = res_resolver.all()
             for alerta in alertas_a_resolver:
                 # --- CORRECCIÓN v5: Cambiar estado_alerta ---
                 alerta.estado_alerta = 'GESTIONADA' # <-- Marcar como gestionada
                 alerta.timestamp_gestion = datetime.now(timezone.utc) # <-- Usar timestamp_gestion
                 # --- FIN CORRECCIÓN v5 ---
                 alerta.notas_resolucion = f"Resuelta automáticamente por inspección con profundidad {profundidad_medida:.1f}mm >= umbral {umbral_minimo:.1f}mm."
                 session.add(alerta)
             if alertas_a_resolver:
                 await session.commit()
                 logger.info(f"Resueltas {len(alertas_a_resolver)} alertas de profundidad baja para neumático {neumatico.id}")

    except Exception as e:
        logger.error(f"Error no crítico en check_profundidad_baja para evento {evento.id}: {e}", exc_info=True)


async def check_stock_minimo(session: AsyncSession, modelo_id: uuid.UUID, almacen_id: uuid.UUID):
    """Verifica si el stock de un modelo en un almacén está bajo el mínimo."""
    try:
        stmt_stock = select(func.count(Neumatico.id)).where(
            Neumatico.estado_actual == EstadoNeumaticoEnum.EN_STOCK,
            Neumatico.modelo_id == modelo_id,
            Neumatico.ubicacion_almacen_id == almacen_id
        )
        result_stock = await session.exec(stmt_stock)
        stock_actual = result_stock.scalar() or 0

        # --- CORRECCIÓN EN LA CONSULTA (v5 - Usar Enum) ---
        stmt_param = select(ParametroInventario).where(
            ParametroInventario.tipo_parametro == TipoParametroEnum.NIVEL_MINIMO, # <-- Usar Enum
            ParametroInventario.modelo_id == modelo_id,
            ParametroInventario.activo == True,
            (ParametroInventario.almacen_id == almacen_id) | (ParametroInventario.almacen_id.is_(None))
        ).order_by(
            ParametroInventario.almacen_id.desc().nulls_last()
        )
        # --- FIN CORRECCIÓN EN LA CONSULTA (v5) ---

        resultado_param = await session.exec(stmt_param)
        parametro = resultado_param.first()

        if not parametro or parametro.valor_numerico is None:
            logger.debug(f"No se encontró nivel mínimo de stock activo para modelo {modelo_id} en almacén {almacen_id}.")
            return

        nivel_minimo = parametro.valor_numerico

        if stock_actual < nivel_minimo:
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
                parametro_id=parametro.id,
                datos_contexto=contexto
            )
        else:
            # --- CORRECCIÓN v5: Usar estado_alerta ---
            stmt_resolver = select(Alerta).where(
                Alerta.tipo_alerta == 'STOCK_MINIMO',
                Alerta.modelo_id == modelo_id,
                Alerta.almacen_id == almacen_id,
                Alerta.estado_alerta != 'GESTIONADA' # <-- Usar estado_alerta
            )
            # --- FIN CORRECCIÓN v5 ---
            res_resolver = await session.exec(stmt_resolver)
            alertas_a_resolver = res_resolver.all()
            for alerta in alertas_a_resolver:
                 # --- CORRECCIÓN v5: Cambiar estado_alerta ---
                 alerta.estado_alerta = 'GESTIONADA' # <-- Marcar como gestionada
                 alerta.timestamp_gestion = datetime.now(timezone.utc) # <-- Usar timestamp_gestion
                 # --- FIN CORRECCIÓN v5 ---
                 alerta.notas_resolucion = f"Resuelta automáticamente. Stock actual {stock_actual} >= mínimo {nivel_minimo:.0f}."
                 session.add(alerta)
            if alertas_a_resolver:
                await session.commit()
                logger.info(f"Resueltas {len(alertas_a_resolver)} alertas de stock mínimo para modelo {modelo_id} en almacén {almacen_id}")

    except Exception as e:
         logger.error(f"Error no crítico en check_stock_minimo para modelo {modelo_id}, almacén {almacen_id}: {e}", exc_info=True)

# --- Fin del archivo ---
