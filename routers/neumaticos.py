# routers/neumaticos.py
import uuid
import logging
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlmodel import select  # Necesario para consultas en leer_historial_neumatico
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import text # Solo para vistas

# --- Dependencias de BD y Autenticación ---
from database import get_session # Nombre correcto de tu función get_session
import auth
from models.usuario import Usuario

# --- Modelos y Schemas (Solo los necesarios para tipos y respuestas del router) ---
from models.neumatico import Neumatico # Para obtener neumático en GET historial
from models.evento_neumatico import EventoNeumatico # Para obtener eventos en GET historial
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem
from schemas.common import TipoEventoNeumaticoEnum # Necesario para lógica de alertas
from pydantic import ValidationError

# --- Servicios ---
# Importar el servicio y sus excepciones personalizadas
from services.neumatico_service import NeumaticoService, NeumaticoNotFoundError, ValidationError as ServiceValidationError, ConflictError as ServiceConflictError
# Importar solo las funciones existentes del servicio de alertas
from services.alert_service import check_profundidad_baja, check_stock_minimo
# --- Configuración del Router ---
router = APIRouter(
    # prefix="/neumaticos", # Sin prefijo si se incluye en main.py con prefijo
    tags=["Neumáticos y Eventos"],
    dependencies=[Depends(auth.get_current_active_user)]
)
logger = logging.getLogger(__name__)

# --- Endpoint PING ---
@router.get("/ping", status_code=status.HTTP_200_OK, summary="Ping de prueba para el router")
async def ping_neumaticos():
    return {"message": "pong desde neumaticos"}

# --- Endpoint CREAR EVENTO (Llama al Servicio) ---
@router.post(
    "/eventos",
    response_model=EventoNeumaticoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo evento para un neumático (vía Servicio)",
    description="Crea un evento y desencadena la actualización del neumático asociado en la capa de servicio."
)
async def crear_evento_neumatico(
    evento_in: EventoNeumaticoCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[Usuario, Depends(auth.get_current_active_user)]
):
    """
    Endpoint para registrar un nuevo evento.
    Delega la lógica de creación y actualización al NeumaticoService.
    Maneja la transacción y las alertas posteriores.
    """
    neumatico_service = NeumaticoService()
    
    try:
        # 1. Llamar al servicio para procesar y añadir a la sesión
        logger.debug(f"Router: Llamando a NeumaticoService para evento {evento_in.tipo_evento.value}, neumático {evento_in.neumatico_id}")
        db_evento, alm_salida, alm_entrada = await neumatico_service.crear_evento_y_actualizar_neumatico(
            evento_in=evento_in,
            current_user=current_user,
            db=session
        )
        logger.debug(f"Router: NeumaticoService retornó evento (pre-commit).")

        # 2. Intentar confirmar la transacción (guarda evento y cambios en neumático)
        logger.debug("Router: Intentando commit...")
        await session.commit()
        logger.debug("Router: Commit exitoso.")

        # 3. Refrescar el objeto evento (importante para obtener IDs/defaults generados por DB)
        try:
             await session.refresh(db_evento)
             logger.debug(f"Router: Evento {db_evento.id} refrescado post-commit.")
             # Podrías refrescar el neumático también si necesitas info actualizada post-commit
             # await session.refresh(await session.get(Neumatico, db_evento.neumatico_id))
        except Exception as refresh_exc:
             logger.error(f"Router: Error al refrescar evento {getattr(db_evento,'id','N/A')} post-commit: {refresh_exc}", exc_info=True)

        # 4. Llamar servicios de alerta (POST-COMMIT)
# 4. Llamar servicios de alerta (POST-COMMIT) - Directamente a las funciones importadas
        try:
            logger.debug(f"Router: Verificando alertas para evento {db_evento.id} tipo {db_evento.tipo_evento.value}")
            # Alerta de Profundidad Baja
            if db_evento.tipo_evento == TipoEventoNeumaticoEnum.INSPECCION and db_evento.profundidad_remanente_mm is not None:
                 logger.debug(f"Router: Llamando check_profundidad_baja para evento {db_evento.id}")
                 await check_profundidad_baja(session, db_evento) # Llama a la función directamente

            # Alertas de Stock Mínimo
            neumatico_afectado = await session.get(Neumatico, db_evento.neumatico_id)
            if neumatico_afectado and neumatico_afectado.modelo_id:
                # ... (lógica para determinar alm_salida, alm_entrada) ...
                if alm_salida:
                    logger.debug(f"Router: Llamando check_stock_minimo (salida) para modelo {neumatico_afectado.modelo_id}, almacén {alm_salida}")
                    await check_stock_minimo(session, neumatico_afectado.modelo_id, alm_salida) # Llama a la función directamente
                if alm_entrada and alm_entrada != alm_salida:
                    logger.debug(f"Router: Llamando check_stock_minimo (entrada) para modelo {neumatico_afectado.modelo_id}, almacén {alm_entrada}")
                    await check_stock_minimo(session, neumatico_afectado.modelo_id, alm_entrada) # Llama a la función directamente
            else:
                 logger.warning(f"Router: No se pudo obtener modelo_id para neumático {db_evento.neumatico_id} post-commit para verificar stock.")

        except Exception as alert_exc:
             logger.error(f"Router: Error no crítico al generar alertas post-evento {db_evento.id}: {alert_exc}", exc_info=True)

        # 5. Devolver respuesta exitosa validada
        logger.info(f"Router: Evento {db_evento.tipo_evento.value} para neumático {db_evento.neumatico_id} procesado exitosamente.")
        return EventoNeumaticoRead.model_validate(db_evento)

    # --- Manejo de Excepciones (Captura excepciones del servicio y de DB) ---
    except (NeumaticoNotFoundError, ServiceValidationError, ServiceConflictError) as service_exc:
        await session.rollback()
        logger.warning(f"Error de servicio capturado en router: {service_exc.message} (Status: {service_exc.status_code})")
        raise HTTPException(status_code=service_exc.status_code, detail=service_exc.message)
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad en router: {str(e)}", exc_info=True)
        detail = "Conflicto de datos. ¿Intentando duplicar información única?"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    except SQLAlchemyError as e:
        await session.rollback()
        pgcode = getattr(e, 'pgcode', 'Genérico')
        logger.error(f"Error SQLAlchemy en router: {str(e)} (Code: {pgcode})", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error de base de datos.")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado en router /eventos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")


# --- Endpoints de Lectura (Sin cambios) ---
@router.get("/{neumatico_id}/historial", response_model=List[EventoNeumaticoRead], summary="Obtener historial de neumático")
async def leer_historial_neumatico(
    neumatico_id: uuid.UUID = Path(..., description="ID del neumático"),
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    # ... (código original sin cambios) ...
    logger.info(f"Solicitando historial para neumático ID: {neumatico_id}")
    neumatico = await session.get(Neumatico, neumatico_id)
    if not neumatico:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Neumático con ID {neumatico_id} no encontrado.")
    try:
        stmt = select(EventoNeumatico).where(EventoNeumatico.neumatico_id == neumatico_id).order_by(EventoNeumatico.timestamp_evento.desc())
        result = await session.exec(stmt)
        eventos = result.all()
        logger.info(f"Encontrados {len(eventos)} eventos para neumático {neumatico_id}")
        return [EventoNeumaticoRead.model_validate(evento) for evento in eventos]
    except Exception as e:
        logger.error(f"Error al leer/validar historial neumático {neumatico_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al procesar el historial.")


@router.get("/instalados", response_model=List[NeumaticoInstaladoItem], summary="Listar neumáticos instalados")
async def leer_neumaticos_instalados(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[Usuario, Depends(auth.get_current_active_user)]
):
    # ... (código original sin cambios usando la vista) ...
    logger.info(f"Usuario {current_user.username} solicitando lista de neumáticos instalados.")
    try:
        from sqlalchemy.sql import text
        query = text("""
            SELECT
                id, neumatico_id, numero_serie, dot, nombre_modelo, medida, fabricante,
                placa, numero_economico, tipo_vehiculo, codigo_posicion,
                profundidad_actual_mm, presion_actual_psi,
                kilometraje_neumatico_acumulado, vida_actual, reencauches_realizados
            FROM vw_neumaticos_instalados_optimizada
        """)
        result = await session.execute(query)
        instalados_data = result.mappings().all()
        logger.info(f"Encontrados {len(instalados_data)} neumáticos instalados desde la vista.")
        validated_items = [NeumaticoInstaladoItem.model_validate(item_data) for item_data in instalados_data]
        return validated_items
    except ValidationError as e:
        logger.error(f"Error validando datos de la vista 'vw_neumaticos_instalados_optimizada' contra el schema: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Inconsistencia entre la vista de BD y el schema esperado.")
    except Exception as e:
        logger.error(f"Error inesperado al leer/validar neumáticos instalados desde la vista: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al procesar neumáticos instalados.")