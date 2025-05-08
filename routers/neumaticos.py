# routers/neumaticos.py (Completo y Corregido v2)
import uuid
import logging
from typing import List, Annotated, Optional # Asegúrate que Annotated esté importado

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func # Para usar func.lower si refinas el check
from sqlalchemy.sql import text # Solo para vistas

# --- Dependencias de BD y Autenticación ---
from core.dependencies import get_session # Usar la dependencia centralizada
from core.dependencies import get_current_active_user # Usar la dependencia centralizada
from models.usuario import Usuario # Modelo de Usuario

# --- Modelos y Schemas ---
from models.neumatico import Neumatico
from models.evento_neumatico import EventoNeumatico
# Importa los schemas necesarios
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem
# Importar Enums desde su ubicación correcta
from models.evento_neumatico import TipoEventoNeumaticoEnum
from pydantic import ValidationError as PydanticValidationError

# --- Servicios ---
# Importar el servicio y sus excepciones personalizadas
from services.neumatico_service import (
    NeumaticoService,
    NeumaticoNotFoundError,
    ValidationError as ServiceValidationError, # Renombrar para evitar conflicto
    ConflictError as ServiceConflictError     # Renombrar para evitar conflicto
)
# !! Ya NO se importan check_profundidad_baja, check_stock_minimo aquí !!

# --- Configuración del Router ---
router = APIRouter(
    tags=["Neumáticos y Eventos"],
    # Aplicar autenticación a todos los endpoints de este router
    dependencies=[Depends(get_current_active_user)] # Usar la dependencia centralizada
)
logger = logging.getLogger(__name__)

# --- Endpoint PING ---
@router.get("/ping", status_code=status.HTTP_200_OK, summary="Ping de prueba para el router")
async def ping_neumaticos():
    """Endpoint simple para verificar que el router de neumáticos está respondiendo."""
    return {"message": "pong desde neumaticos"}

# --- Endpoint CREAR EVENTO (Llama al Servicio) ---
# ... (importaciones y definición del router van antes) ...

@router.post(
    "/eventos",
    response_model=EventoNeumaticoRead, # Schema de respuesta
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo evento para un neumático (vía Servicio)",
    description="Crea un evento y desencadena la actualización del neumático asociado en la capa de servicio."
)
async def crear_evento_neumatico(
    evento_in: EventoNeumaticoCreate, # Schema de entrada
    session: Annotated[AsyncSession, Depends(get_session)], # Dependencia de Sesión
    current_user: Annotated[Usuario, Depends(get_current_active_user)] # Usar la dependencia centralizada
):
    """
    Endpoint para registrar un nuevo evento de neumático.
    Delega toda la lógica de negocio y actualizaciones al NeumaticoService.
    Maneja la transacción y las excepciones.
    """
    neumatico_service = NeumaticoService(session=session) # Correcto

    # Asignar usuario actual si es necesario
    # (El servicio también lo usa ahora)
    if evento_in.usuario_id is None:
        evento_in.usuario_id = current_user.id
    if hasattr(evento_in, 'creado_por') and evento_in.creado_por is None:
         evento_in.creado_por = current_user.id

    try:
        # --- *** CORRECCIÓN EN LA LLAMADA AL SERVICIO *** ---
        logger.info(f"Router: Iniciando procesamiento de evento {evento_in.tipo_evento.value} para neumático {evento_in.neumatico_id or evento_in.numero_serie}")
        neumatico_actualizado, evento_creado = await neumatico_service.registrar_evento(
            evento_in=evento_in,
            current_user=current_user # <-- Pasar el usuario actual aquí
        )
        # --- *** FIN CORRECCIÓN *** ---
        logger.info(f"Router: Servicio completado para evento ID (pre-commit): {evento_creado.id}")

        # Commit de la transacción principal aquí (si no usas un middleware de sesión)
        await session.commit()
        logger.info(f"Router: Commit exitoso para evento ID (pre-refresh): {evento_creado.id}")

        # Refrescar para obtener datos generados por DB
        await session.refresh(evento_creado)
        # await session.refresh(neumatico_actualizado) # Opcional

        logger.info(f"Router: Evento {evento_creado.id} ({evento_creado.tipo_evento.value}) registrado exitosamente.")
        # Devolver respuesta validada por el schema Read
        return EventoNeumaticoRead.model_validate(evento_creado)

    except (NeumaticoNotFoundError, ServiceValidationError, ServiceConflictError) as service_exc:
        await session.rollback()
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if isinstance(service_exc, NeumaticoNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(service_exc, ServiceValidationError):
             status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        elif isinstance(service_exc, ServiceConflictError):
            status_code = status.HTTP_409_CONFLICT
        logger.warning(f"Error de servicio manejado en router /eventos: {service_exc.message} (Status Code: {status_code})")
        raise HTTPException(status_code=status_code, detail=service_exc.message)
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad BD en router /eventos: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de datos al guardar.")
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Error SQLAlchemy en router /eventos: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error inesperado en BD.")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado en router /eventos: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")

# ... (resto del router) ...


# --- Endpoints de Lectura ---
@router.get(
    "/{neumatico_id}/historial",
    response_model=List[HistorialNeumaticoItem], # Usa el schema correcto para el historial
    summary="Obtener historial de eventos para un neumático"
)
async def leer_historial_neumatico(
    # --- PARÁMETROS REORDENADOS PARA EVITAR WARNING PYLANCE ---
    session: Annotated[AsyncSession, Depends(get_session)], # Primero la sesión
    neumatico_id: uuid.UUID = Path(..., description="ID del neumático") # Luego el ID de la ruta
    # --- FIN REORDENAMIENTO ---
):
    """Obtiene la lista de eventos históricos para un neumático específico, ordenados por fecha descendente."""
    logger.info(f"Solicitando historial para neumático ID: {neumatico_id}")
    # Verificar si el neumático existe
    neumatico = await session.get(Neumatico, neumatico_id)
    if not neumatico:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Neumático con ID {neumatico_id} no encontrado.")

    # Obtener historial usando el servicio
    try:
        neumatico_service = NeumaticoService(session=session) # Instanciar servicio
        eventos = await neumatico_service.get_historial(neumatico_id)
        logger.info(f"Encontrados {len(eventos)} eventos para neumático {neumatico_id} (vía servicio)")
        # Validar con el schema de respuesta
        return [HistorialNeumaticoItem.model_validate(evento) for evento in eventos]
    except PydanticValidationError as e:
         logger.error(f"Error validando eventos del historial para neumático {neumatico_id}: {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al procesar datos del historial.")
    except Exception as e:
        logger.error(f"Error inesperado al leer historial neumático {neumatico_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al obtener historial.")

# ... (el resto de las funciones del router van aquí) ...

@router.get(
    "/instalados",
    response_model=List[NeumaticoInstaladoItem], # Usa el schema correcto para instalados
    summary="Listar todos los neumáticos actualmente instalados"
)
async def leer_neumaticos_instalados(
    session: Annotated[AsyncSession, Depends(get_session)],
    # current_user: Usuario = Depends(get_current_active_user) # Ya está en dependencies
):
    """Obtiene la lista de neumáticos instalados desde la vista optimizada `vw_neumaticos_instalados_optimizada`."""
    logger.info(f"Solicitando lista de neumáticos instalados.")
    # Importar el objeto CRUD de neumático si no está ya importado
    from crud.crud_neumatico import neumatico as crud_neumatico # Importar aquí o al inicio

    try:
        # Obtener datos de la vista usando el CRUD
        instalados_data = await crud_neumatico.get_neumaticos_instalados(session)
        logger.info(f"Encontrados {len(instalados_data)} neumáticos instalados desde la vista (vía CRUD).")
        # Validar cada fila contra el schema Pydantic
        validated_items = [NeumaticoInstaladoItem.model_validate(item_data) for item_data in instalados_data]
        return validated_items
    except PydanticValidationError as e:
        logger.error(f"Error validando datos de la vista 'vw_neumaticos_instalados_optimizada': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inconsistencia entre la vista de BD y el schema esperado para neumáticos instalados."
        )
    except Exception as e:
        logger.error(f"Error inesperado al leer neumáticos instalados desde la vista: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar neumáticos instalados."
        )