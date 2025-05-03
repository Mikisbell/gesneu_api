# routers/neumaticos.py
import uuid
import logging
from datetime import date, datetime, timezone
from typing import List, Annotated, Optional, Dict, Any # Añadir Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import text

# --- Dependencias de BD y Autenticación ---
from database import get_session
import auth
from models.usuario import Usuario

# --- Modelos y Schemas ---
from models.neumatico import Neumatico, EstadoNeumaticoEnum
from models.evento_neumatico import EventoNeumatico
from models.vehiculo import Vehiculo
from models.tipo_vehiculo import TipoVehiculo
from models.posicion_neumatico import PosicionNeumatico, LadoVehiculoEnum
from models.almacen import Almacen
from models.motivo_desecho import MotivoDesecho
from models.modelo import ModeloNeumatico
from models.configuracion_eje import ConfiguracionEje

from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem
from schemas.common import TipoEventoNeumaticoEnum
# --- Servicios ---
from services.alert_service import check_profundidad_baja, check_stock_minimo
# Quitar la importación del servicio si ponemos la lógica aquí
# from services.neumatico_service import process_reencauche_salida_event

from pydantic import ValidationError

# --- Configuración del Router ---
router = APIRouter(
    # prefix="/neumaticos", # SIN PREFIJO AQUÍ
    tags=["Neumáticos y Eventos"],
    dependencies=[Depends(auth.get_current_active_user)]
)
logger = logging.getLogger(__name__)

# --- Endpoint PING ---
@router.get("/ping", status_code=status.HTTP_200_OK, summary="Ping de prueba para el router")
async def ping_neumaticos():
    return {"message": "pong desde neumaticos"}

# --- Endpoint CREAR EVENTO (Refactorizado v2) ---
@router.post(
    "/eventos",
    response_model=EventoNeumaticoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo evento y actualizar neumático",
    description="Crea un evento y actualiza el estado/ubicación/info del neumático si aplica."
)
async def crear_evento_neumatico(
    evento_in: EventoNeumaticoCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[Usuario, Depends(auth.get_current_active_user)]
):
    """Registra un nuevo evento y actualiza el neumático asociado."""

    db_evento = EventoNeumatico.model_validate(
        evento_in,
        update={"usuario_id": current_user.id}
    )
    db_evento.timestamp_evento = datetime.now(timezone.utc)

    neumatico_modificado = False
    modelo_afectado_stock: Optional[uuid.UUID] = None
    almacen_afectado_stock_entrada: Optional[uuid.UUID] = None
    almacen_afectado_stock_salida: Optional[uuid.UUID] = None
    almacen_destino_id: Optional[uuid.UUID] = evento_in.almacen_destino_id # Usar el del payload

    try:
        logger.info(f"Router: Procesando evento {db_evento.tipo_evento.value} para neumático ID {db_evento.neumatico_id}")

        neumatico = await session.get(Neumatico, db_evento.neumatico_id)
        if not neumatico:
            raise HTTPException(status_code=404, detail="Neumático no encontrado")

        logger.debug(f"Neumático {neumatico.id} encontrado. Estado ANTES: {neumatico.estado_actual.value if neumatico.estado_actual else 'None'}")
        estado_original = neumatico.estado_actual # Guardar estado original para comparación
        nuevo_estado_asignado: Optional[EstadoNeumaticoEnum] = None # Estado que asignaremos en código


        # --- LÓGICA ESPECÍFICA POR TIPO DE EVENTO (Con estado explícito) ---

        if db_evento.tipo_evento == TipoEventoNeumaticoEnum.INSTALACION:
            if not db_evento.vehiculo_id or not db_evento.posicion_id: raise HTTPException(status_code=422, detail="Vehiculo ID y Posicion ID requeridos.")
            if neumatico.estado_actual != EstadoNeumaticoEnum.EN_STOCK: raise HTTPException(status_code=409, detail=f"Neumático debe estar EN_STOCK (estado actual: {neumatico.estado_actual.value}).")
            # Validaciones de Vehiculo/Posición/RF16 (asumimos OK por brevedad)
            # ...
            nuevo_estado_asignado = EstadoNeumaticoEnum.INSTALADO
            modelo_afectado_stock = neumatico.modelo_id
            almacen_afectado_stock_salida = neumatico.ubicacion_almacen_id
            neumatico.ubicacion_actual_vehiculo_id = db_evento.vehiculo_id
            neumatico.ubicacion_actual_posicion_id = db_evento.posicion_id
            neumatico.ubicacion_almacen_id = None
            neumatico.kilometraje_acumulado = 0 # Resetear KM al instalar


        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.DESMONTAJE:
            if neumatico.estado_actual != EstadoNeumaticoEnum.INSTALADO: raise HTTPException(status_code=409, detail="Solo se pueden desmontar neumáticos INSTALADOS.")
            if not db_evento.destino_desmontaje: raise HTTPException(status_code=422, detail="destino_desmontaje es requerido.")

            nuevo_estado_asignado = db_evento.destino_desmontaje # Estado destino viene del payload

            if nuevo_estado_asignado != EstadoNeumaticoEnum.DESECHADO:
                if not almacen_destino_id: raise HTTPException(status_code=422, detail="ID de almacén destino requerido si destino no es DESECHADO.")
                almacen_destino_db = await session.get(Almacen, almacen_destino_id)
                if not almacen_destino_db or not almacen_destino_db.activo: raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")
                neumatico.ubicacion_almacen_id = almacen_destino_id
                almacen_afectado_stock_entrada = almacen_destino_id
            else: # Destino es DESECHADO
                if not db_evento.motivo_desecho_id_evento: raise HTTPException(status_code=422, detail="motivo_desecho_id_evento es requerido para DESMONTAJE a DESECHADO.")
                motivo = await session.get(MotivoDesecho, db_evento.motivo_desecho_id_evento)
                if not motivo: raise HTTPException(status_code=404, detail=f"Motivo desecho ID {db_evento.motivo_desecho_id_evento} no encontrado.")
                neumatico.motivo_desecho_id = db_evento.motivo_desecho_id_evento
                neumatico.fecha_desecho = db_evento.timestamp_evento.date()
                neumatico.ubicacion_almacen_id = None

            # Actualizar KM acumulado (requiere odómetro actual del vehículo)
            # Esta lógica debería estar idealmente en un servicio o aquí si se pasa el odómetro actual del vehículo
            if db_evento.odometro_vehiculo_en_evento is not None:
                # Necesitamos el evento de instalación previo para calcular diferencia
                stmt_install = select(EventoNeumatico).where(
                    EventoNeumatico.neumatico_id == neumatico.id,
                    EventoNeumatico.tipo_evento == TipoEventoNeumaticoEnum.INSTALACION
                ).order_by(EventoNeumatico.timestamp_evento.desc()).limit(1)
                last_install_event = (await session.exec(stmt_install)).first()
                if last_install_event and last_install_event.odometro_vehiculo_en_evento is not None:
                     km_recorridos = db_evento.odometro_vehiculo_en_evento - last_install_event.odometro_vehiculo_en_evento
                     if km_recorridos >= 0:
                         neumatico.kilometraje_acumulado = (neumatico.kilometraje_acumulado or 0) + km_recorridos
                         logger.debug(f"KM acumulados actualizados a: {neumatico.kilometraje_acumulado}")
                     else: logger.warning("Odómetro de desmontaje menor que el de instalación, no se actualiza KM.")
                else: logger.warning("No se encontró evento de instalación o su odómetro para calcular KM.")

            neumatico.ubicacion_actual_vehiculo_id = None
            neumatico.ubicacion_actual_posicion_id = None

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.DESECHO:
            if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO: raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede desechar un neumático INSTALADO. Realiza DESMONTAJE primero.")
            motivo_id_recibido = evento_in.motivo_desecho_id_evento
            if not motivo_id_recibido: raise HTTPException(status_code=422, detail="motivo_desecho_id_evento es requerido.")
            motivo = await session.get(MotivoDesecho, motivo_id_recibido)
            if not motivo: raise HTTPException(status_code=404, detail=f"Motivo desecho ID {motivo_id_recibido} no encontrado.")

            nuevo_estado_asignado = EstadoNeumaticoEnum.DESECHADO
            neumatico.motivo_desecho_id = motivo_id_recibido
            neumatico.fecha_desecho = db_evento.timestamp_evento.date()
            almacen_afectado_stock_salida = neumatico.ubicacion_almacen_id # Sale de donde estuviera
            neumatico.ubicacion_actual_vehiculo_id = None
            neumatico.ubicacion_actual_posicion_id = None
            neumatico.ubicacion_almacen_id = None

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.ROTACION:
             if neumatico.estado_actual != EstadoNeumaticoEnum.INSTALADO: raise HTTPException(status_code=409, detail="Solo se pueden rotar neumáticos INSTALADOS.")
             if not db_evento.vehiculo_id or not db_evento.posicion_id: raise HTTPException(status_code=422, detail="Vehiculo ID y Posicion ID de destino requeridos.")
             posicion_destino = await session.get(PosicionNeumatico, db_evento.posicion_id)
             if not posicion_destino: raise HTTPException(status_code=404, detail=f"Posición destino ID {db_evento.posicion_id} no encontrada.")
             # TODO: Validar compatibilidad

             # El estado NO cambia
             nuevo_estado_asignado = EstadoNeumaticoEnum.INSTALADO
             neumatico.ubicacion_actual_vehiculo_id = db_evento.vehiculo_id
             neumatico.ubicacion_actual_posicion_id = db_evento.posicion_id

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REPARACION_ENTRADA:
            if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO: raise HTTPException(status_code=409, detail="Desmonta el neumático antes de enviarlo a reparar.")
            # Validar almacén taller (omitido por brevedad)
            # ...
            nuevo_estado_asignado = EstadoNeumaticoEnum.EN_REPARACION
            almacen_afectado_stock_salida = neumatico.ubicacion_almacen_id
            neumatico.ubicacion_almacen_id = almacen_destino_id
            neumatico.ubicacion_actual_vehiculo_id = None
            neumatico.ubicacion_actual_posicion_id = None

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REPARACION_SALIDA:
            if neumatico.estado_actual != EstadoNeumaticoEnum.EN_REPARACION: raise HTTPException(status_code=409, detail="El neumático debe estar EN_REPARACION.")
            if not almacen_destino_id: raise HTTPException(status_code=422, detail="ID de almacén destino requerido.")
            almacen_destino_db = await session.get(Almacen, almacen_destino_id)
            if not almacen_destino_db or not almacen_destino_db.activo: raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")

            nuevo_estado_asignado = EstadoNeumaticoEnum.EN_STOCK
            neumatico.ubicacion_almacen_id = almacen_destino_id
            almacen_afectado_stock_entrada = almacen_destino_id

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA:
            if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO: raise HTTPException(status_code=409, detail="Desmonta el neumático antes de enviarlo a reencauche.")
            # Validar almacén reencauchadora (omitido por brevedad)
            # ...
            nuevo_estado_asignado = EstadoNeumaticoEnum.EN_REENCAUCHE
            almacen_afectado_stock_salida = neumatico.ubicacion_almacen_id
            neumatico.ubicacion_almacen_id = almacen_destino_id # ID de la reencauchadora
            neumatico.ubicacion_actual_vehiculo_id = None
            neumatico.ubicacion_actual_posicion_id = None

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA:
            if neumatico.estado_actual != EstadoNeumaticoEnum.EN_REENCAUCHE: raise HTTPException(status_code=409, detail="El neumático debe estar EN_REENCAUCHE.")
            if evento_in.profundidad_post_reencauche_mm is None: raise HTTPException(status_code=422, detail="profundidad_post_reencauche_mm es requerida.")
            if not almacen_destino_id: raise HTTPException(status_code=422, detail="ID de almacén destino requerido.")
            almacen_destino_db = await session.get(Almacen, almacen_destino_id)
            if not almacen_destino_db or not almacen_destino_db.activo: raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")

            # --- Lógica Manual para Reencauche Salida (CORREGIDA) ---
            nuevo_estado_asignado = EstadoNeumaticoEnum.EN_STOCK
            neumatico.reencauches_realizados = (neumatico.reencauches_realizados or 0) + 1
            neumatico.vida_actual = (neumatico.vida_actual or 0) + 1
            neumatico.es_reencauchado = True
            neumatico.profundidad_inicial_mm = evento_in.profundidad_post_reencauche_mm
            neumatico.kilometraje_acumulado = 0 # Resetear KM
            neumatico.ubicacion_almacen_id = almacen_destino_id # Mover a almacén destino
            almacen_afectado_stock_entrada = almacen_destino_id
            logger.info(f"Reencauche Salida: Neumático {neumatico.id} actualizado a EN_STOCK, {neumatico.reencauches_realizados} reenc., vida {neumatico.vida_actual}, prof {neumatico.profundidad_inicial_mm}mm")
            # ----------------------------------------------------------

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.TRANSFERENCIA_UBICACION:
             if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO: raise HTTPException(status_code=409, detail="No se puede transferir un neumático INSTALADO.")
             if neumatico.ubicacion_almacen_id is None: raise HTTPException(status_code=409, detail="El neumático no está en un almacén de origen.")
             if not almacen_destino_id: raise HTTPException(status_code=422, detail="ID de almacén destino requerido.")
             if almacen_destino_id == neumatico.ubicacion_almacen_id: raise HTTPException(status_code=400, detail="Almacén de origen y destino son iguales.")
             almacen_destino_db = await session.get(Almacen, almacen_destino_id)
             if not almacen_destino_db or not almacen_destino_db.activo: raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")

             almacen_origen_id = neumatico.ubicacion_almacen_id
             neumatico.ubicacion_almacen_id = almacen_destino_id # Actualizar ubicación
             almacen_afectado_stock_salida = almacen_origen_id
             almacen_afectado_stock_entrada = almacen_destino_id
             # El estado no cambia
             nuevo_estado_asignado = neumatico.estado_actual # Asegurar que se mantenga el estado actual

        # --- Actualización Final del Neumático (SIEMPRE) ---
        if nuevo_estado_asignado is not None and neumatico.estado_actual != nuevo_estado_asignado:
             logger.info(f"Cambiando estado neumático {neumatico.id} de {neumatico.estado_actual.value} a {nuevo_estado_asignado.value}")
             neumatico.estado_actual = nuevo_estado_asignado
             neumatico_modificado = True

        # Siempre actualizar campos de auditoría y fecha si hubo alguna modificación lógica
        if neumatico_modificado:
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico.actualizado_en = datetime.now(timezone.utc)
            neumatico.actualizado_por = current_user.id
            # ¡NO HACER session.add(neumatico) aquí! Dejar que SQLAlchemy lo detecte.

        # --- Guardar Evento y Cambios en Neumático ---
        logger.debug(f"Añadiendo evento {db_evento.id} a la sesión.")
        session.add(db_evento)

        logger.debug("Intentando flush...")
        await session.flush([db_evento, neumatico] if neumatico_modificado else [db_evento]) # Flush explícito ANTES de commit
        logger.debug("Flush exitoso.")

        logger.debug("Intentando commit final de la sesión...")
        await session.commit()
        logger.debug("Commit final exitoso.")

        # --- Refrescar y verificar (Opcional pero bueno para debug) ---
        try:
            await session.refresh(db_evento)
            # Refrescar neumático solo si esperamos que haya cambiado
            if neumatico_modificado:
                await session.refresh(neumatico)
                logger.debug(f"Neumático {neumatico.id} refrescado. Estado final: {neumatico.estado_actual.value if neumatico.estado_actual else 'None'}")
                # Comprobación interna post-commit (opcional, para debug extremo)
                if nuevo_estado_asignado and neumatico.estado_actual != nuevo_estado_asignado:
                     logger.error(f"¡¡INCONSISTENCIA DETECTADA POST-COMMIT!! Estado esperado={nuevo_estado_asignado.value}, Estado real={neumatico.estado_actual.value}")
                     # Podrías lanzar un error aquí si quieres que falle en este punto
                     # raise HTTPException(status_code=500, detail="Error interno: Fallo la persistencia del estado.")

        except Exception as refresh_exc:
            logger.error(f"Error al refrescar objetos post-commit: {refresh_exc}", exc_info=True)


        # --- Llamada al Servicio de Alertas (después del commit exitoso) ---
        try:
            modelo_afectado_stock = neumatico.modelo_id # Usar el ID del modelo del neumático
            # Chequear stock mínimo en almacén de salida (si hubo)
            if almacen_afectado_stock_salida:
                 logger.debug(f"Llamando check_stock_minimo (salida) para modelo {modelo_afectado_stock}, almacén {almacen_afectado_stock_salida}")
                 await check_stock_minimo(session, modelo_afectado_stock, almacen_afectado_stock_salida)
            # Chequear stock mínimo en almacén de entrada (si hubo)
            if almacen_afectado_stock_entrada and almacen_afectado_stock_entrada != almacen_afectado_stock_salida:
                 logger.debug(f"Llamando check_stock_minimo (entrada) para modelo {modelo_afectado_stock}, almacén {almacen_afectado_stock_entrada}")
                 await check_stock_minimo(session, modelo_afectado_stock, almacen_afectado_stock_entrada)

            # Alerta de Profundidad Baja
            if db_evento.tipo_evento == TipoEventoNeumaticoEnum.INSPECCION and db_evento.profundidad_remanente_mm is not None:
                 logger.debug(f"Llamando check_profundidad_baja para evento {db_evento.id}")
                 await check_profundidad_baja(session, db_evento)

        except Exception as alert_exc:
             logger.error(f"Error no crítico al generar alertas post-evento {db_evento.id}: {alert_exc}", exc_info=True)

        # 8. Preparar y devolver la respuesta
        logger.info(f"Evento {db_evento.tipo_evento.value} para neumático {neumatico.id} procesado exitosamente.")
        return EventoNeumaticoRead.model_validate(db_evento)

    # --- Manejo de Excepciones General ---
    except HTTPException as http_exc:
         await session.rollback()
         logger.warning(f"HTTPException {http_exc.status_code}: {http_exc.detail}")
         raise http_exc
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad: {str(e)}", exc_info=True)
        # ... (manejo detallado si es necesario) ...
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad de datos.")
    except SQLAlchemyError as e:
        await session.rollback()
        pgcode = getattr(e, 'pgcode', 'Genérico')
        logger.error(f"Error SQLAlchemy: {str(e)} (Code: {pgcode})", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error de base de datos.")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado procesando evento: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")

# --- Endpoints de Lectura (Sin cambios significativos) ---
@router.get("/{neumatico_id}/historial", response_model=List[EventoNeumaticoRead], summary="Obtener historial de neumático")
async def leer_historial_neumatico(
    neumatico_id: uuid.UUID = Path(..., description="ID del neumático"),
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    # ... (código sin cambios) ...
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
    # ... (código usando vista, sin cambios) ...
    logger.info(f"Usuario {current_user.username} solicitando lista de neumáticos instalados.")
    try:
        query = text("""
            SELECT
                id, neumatico_id, numero_serie, dot, nombre_modelo, medida, fabricante,
                placa, numero_economico, tipo_vehiculo, codigo_posicion,
                profundidad_actual_mm, presion_actual_psi,
                kilometraje_neumatico_acumulado, vida_actual, reencauches_realizados
            FROM vw_neumaticos_instalados_optimizada
        """)
        result = await session.exec(query)
        try:
             instalados_data = result.mappings().all()
        except AttributeError:
             logger.warning("result.mappings() no disponible, usando result.all() y conversión manual.")
             rows = result.all()
             column_names = result.keys()
             instalados_data = [dict(zip(column_names, row)) for row in rows]

        logger.info(f"Encontrados {len(instalados_data)} neumáticos instalados desde la vista.")
        validated_items = []
        for item_data in instalados_data:
            try:
                item_dict = dict(item_data)
                validated_item = NeumaticoInstaladoItem.model_validate(item_dict)
                validated_items.append(validated_item)
            except ValidationError as e:
                logger.error(f"Error validando item de vista: {item_dict}\nError Pydantic: {e}", exc_info=False)
                raise ValueError(f"Error de validación para item {item_dict.get('numero_serie') or item_dict.get('id')}")

        return validated_items
    except SQLAlchemyError as e:
        logger.error(f"Error DB al consultar vista 'vw_neumaticos_instalados_optimizada': {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al recuperar neumáticos instalados (verificar vista DB).")
    except ValueError as val_err:
        logger.error(f"Error validando datos de la vista contra el schema: {val_err}", exc_info=False)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor al procesar datos de neumáticos.")
    except Exception as e:
        logger.error(f"Error inesperado al leer/validar neumáticos instalados: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor al procesar neumáticos instalados.")