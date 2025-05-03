# services/neumatico_service.py
import uuid
import logging
from datetime import datetime, timezone

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

# Importar Modelos y Schemas necesarios
from models.neumatico import Neumatico, EstadoNeumaticoEnum
from models.modelo import ModeloNeumatico
from models.almacen import Almacen
from models.usuario import Usuario
from schemas.evento_neumatico import EventoNeumaticoCreate # Para acceder a datos del evento

logger = logging.getLogger(__name__)

async def process_reencauche_salida_event(
    session: AsyncSession,
    evento_data: EventoNeumaticoCreate, # Usamos el schema de entrada
    neumatico: Neumatico,
    current_user: Usuario
):
    """
    Procesa la lógica para un evento REENCAUCHE_SALIDA.
    Actualiza el neumático directamente y realiza validaciones.
    """
    logger.info(f"Servicio: Procesando REENCAUCHE_SALIDA para neumático ID: {neumatico.id}")

    # --- Validaciones previas (movidas o adaptadas del router/trigger) ---
    if neumatico.estado_actual != EstadoNeumaticoEnum.EN_REENCAUCHE:
        logger.warning(f"Intento de salida de reencauche para neumático {neumatico.id} no en estado EN_REENCAUCHE (estado: {neumatico.estado_actual}).")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El neumático debe estar EN_REENCAUCHE para procesar la salida.")

    if evento_data.profundidad_post_reencauche_mm is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="profundidad_post_reencauche_mm es requerida para REENCAUCHE_SALIDA.")

    almacen_destino_id = evento_data.almacen_destino_id
    if not almacen_destino_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ID de almacén destino requerido para salida de reencauche.")

    almacen_destino_db = await session.get(Almacen, almacen_destino_id)
    if not almacen_destino_db or not almacen_destino_db.activo:
        logger.warning(f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo para salida reencauche neumático {neumatico.id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")

    # --- Validación Límite Reencauches ---
    modelo = await session.get(ModeloNeumatico, neumatico.modelo_id)
    if not modelo:
        # Manejar caso donde el modelo no existe (aunque FK debería prevenirlo)
        logger.error(f"Modelo ID {neumatico.modelo_id} asociado al neumático {neumatico.id} no encontrado.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error de consistencia: Modelo de neumático no encontrado.")

    # Asegurar valores no nulos para comparación
    reencauches_actuales = neumatico.reencauches_realizados or 0
    max_reencauches = modelo.reencauches_maximos if modelo.reencauches_maximos is not None else 99 # Usar un valor alto si es NULL

    if reencauches_actuales >= max_reencauches:
        logger.warning(f"Neumático {neumatico.id} ha alcanzado/superado el límite de {max_reencauches} reencauches (actual: {reencauches_actuales}).")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Límite de {max_reencauches} reencauches alcanzado/superado ({reencauches_actuales}). No se puede procesar salida."
        )

    # --- Actualización del Neumático (Lógica movida del trigger) ---
    logger.debug(f"Actualizando neumático {neumatico.id} post-reencauche...")
    neumatico.reencauches_realizados = reencauches_actuales + 1
    neumatico.vida_actual = (neumatico.vida_actual or 1) + 1 # Asumiendo que empieza en 1
    neumatico.estado_actual = EstadoNeumaticoEnum.EN_STOCK
    neumatico.kilometraje_acumulado = 0 # Resetear KM
    neumatico.profundidad_inicial_mm = evento_data.profundidad_post_reencauche_mm # Nueva profundidad inicial
    neumatico.es_reencauchado = True
    neumatico.ubicacion_almacen_id = almacen_destino_id # Asignar almacén destino
    neumatico.ubicacion_actual_vehiculo_id = None # Limpiar ubicación vehículo
    neumatico.ubicacion_actual_posicion_id = None # Limpiar ubicación posición

    # --- Actualización de campos de auditoría/evento ---
    now_utc = datetime.now(timezone.utc)
    neumatico.fecha_ultimo_evento = now_utc # Actualizar con timestamp actual
    neumatico.actualizado_en = now_utc
    neumatico.actualizado_por = current_user.id

    logger.info(f"Neumático {neumatico.id} actualizado por servicio REENCAUCHE_SALIDA. Nuevo estado: {neumatico.estado_actual}, Reencauches: {neumatico.reencauches_realizados}")

    # El objeto 'neumatico' ha sido modificado. El router se encargará de añadirlo a la sesión.

# Puedes añadir aquí funciones para procesar otros eventos si decides refactorizar más