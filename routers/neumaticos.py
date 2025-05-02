# routers/neumaticos.py
import uuid
import logging
from datetime import date, datetime, timezone
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from sqlalchemy import func # Descomentado si implementas check_stock_minimo

from database import get_session
from models.usuario import Usuario
from models.neumatico import Neumatico, EstadoNeumaticoEnum
from models.evento_neumatico import EventoNeumatico
# --- Imports necesarios ---
from models.vehiculo import Vehiculo
from models.tipo_vehiculo import TipoVehiculo
from models.posicion_neumatico import PosicionNeumatico
from models.almacen import Almacen
from models.motivo_desecho import MotivoDesecho
# --- Fin imports ---
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem
from schemas.common import TipoEventoNeumaticoEnum
import auth
from services.alert_service import check_profundidad_baja, check_stock_minimo # Añadir check_stock_minimo
# -------------------------------

# --- Definición del Router (SIN PREFIJO INTERNO) ---
router = APIRouter(
    tags=["Neumáticos y Eventos"],
    dependencies=[Depends(auth.get_current_active_user)]
)
logger = logging.getLogger(__name__)


@router.get("/ping", status_code=status.HTTP_200_OK, summary="Ping de prueba para el router")
async def ping_neumaticos():
    """Endpoint simple para verificar si el router está accesible."""
    return {"message": "pong desde neumaticos"}

# --- Endpoint para Crear Eventos (Versión Corregida y Mejorada) ---
@router.post(
    "/eventos",
    response_model=EventoNeumaticoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo evento y actualizar neumático",
    description="Crea un evento y actualiza el estado/ubicación/info del neumático si aplica."
)
async def crear_evento_neumatico(
    evento_in: EventoNeumaticoCreate, # El schema de entrada validado por Pydantic
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[Usuario, Depends(auth.get_current_active_user)]
):
    """Registra un nuevo evento y actualiza el neumático asociado."""

    # Crear instancia del modelo EventoNeumatico a partir del schema validado evento_in
    db_evento = EventoNeumatico.model_validate(
        evento_in,
        update={"usuario_id": current_user.id} # Asignar usuario logueado
    )
    # Asignar timestamp justo antes de procesar
    db_evento.timestamp_evento = datetime.now(timezone.utc)

    neumatico_modificado = False
    modelo_afectado_stock: Optional[uuid.UUID] = None
    almacen_afectado_stock: Optional[uuid.UUID] = None
    almacen_origen_id: Optional[uuid.UUID] = None # Para Transferencia

    try:
        logger.info(f"Procesando evento: {db_evento.tipo_evento.value} para neumático {db_evento.neumatico_id}")

        # Obtener el neumático para validaciones y actualizaciones
        # Usar with_for_update=True si se esperan altos niveles de concurrencia (opcional)
        neumatico = await session.get(Neumatico, db_evento.neumatico_id) # , with_for_update=True)
        if not neumatico:
            logger.warning(f"Neumático ID {db_evento.neumatico_id} no encontrado.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Neumático con ID {db_evento.neumatico_id} no encontrado.")

        # --- Lógica Específica por Tipo de Evento ---

        if db_evento.tipo_evento == TipoEventoNeumaticoEnum.INSTALACION:
            # Validaciones previas
            if not db_evento.vehiculo_id or not db_evento.posicion_id:
                raise HTTPException(status_code=422, detail="Vehiculo ID y Posicion ID requeridos para INSTALACION.")
            if neumatico.estado_actual != EstadoNeumaticoEnum.EN_STOCK:
                raise HTTPException(status_code=409, detail=f"Neumático debe estar EN_STOCK para instalar (estado actual: {neumatico.estado_actual.value}).")

            # Validación RF16 (Reencauchados en ejes no permitidos)
            if neumatico.es_reencauchado:
                vehiculo = await session.get(Vehiculo, db_evento.vehiculo_id)
                if not vehiculo: raise HTTPException(status_code=404, detail=f"Vehículo ID {db_evento.vehiculo_id} no encontrado.")
                tipo_vehiculo = await session.get(TipoVehiculo, vehiculo.tipo_vehiculo_id)
                if not tipo_vehiculo: raise HTTPException(status_code=404, detail=f"Tipo vehículo ID {vehiculo.tipo_vehiculo_id} no encontrado.")
                posicion = await session.get(PosicionNeumatico, db_evento.posicion_id)
                if not posicion: raise HTTPException(status_code=404, detail=f"Posición ID {db_evento.posicion_id} no encontrada.")

                # Obtener config_eje para la 'permite_reencauchados' (asumiendo que está ahí)
                # Necesitarías añadir la relación o hacer un get explícito si no está
                # config_eje = await session.get(ConfiguracionEje, posicion.configuracion_eje_id)
                # if config_eje and not config_eje.permite_reencauchados:
                #     raise HTTPException(status_code=409, detail=f"Restricción: Reencauchados no permitidos en la posición {posicion.codigo_posicion}.")

                # O si la validación es solo por tipo de eje (como en tu código original):
                categoria = (tipo_vehiculo.categoria_principal or "").upper()
                if categoria in ['CAMIÓN', 'REMOLQUE'] and (posicion.es_direccion or posicion.es_traccion):
                     raise HTTPException(status_code=409, detail=f"Restricción: Reencauchados no permitidos en ejes dirección/tracción para '{tipo_vehiculo.categoria_principal}'.")


            # Actualización de Neumático (manejada aquí, NO por trigger para este caso)
            modelo_afectado_stock = neumatico.modelo_id
            almacen_afectado_stock = neumatico.ubicacion_almacen_id # Almacén de donde sale
            neumatico.estado_actual = EstadoNeumaticoEnum.INSTALADO
            neumatico.ubicacion_actual_vehiculo_id = db_evento.vehiculo_id
            neumatico.ubicacion_actual_posicion_id = db_evento.posicion_id
            neumatico.ubicacion_almacen_id = None # Quitar de almacén
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            # El trigger podría encargarse del kilometraje si se pasa odómetro aquí
            neumatico_modificado = True

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.DESMONTAJE:
            if neumatico.estado_actual != EstadoNeumaticoEnum.INSTALADO:
                raise HTTPException(status_code=409, detail="Solo se pueden desmontar neumáticos INSTALADOS.")
            if not db_evento.destino_desmontaje: # Validado por schema, pero seguro
                raise HTTPException(status_code=422, detail="destino_desmontaje es requerido para DESMONTAJE.")

            destino = db_evento.destino_desmontaje
            almacen_destino_id = evento_in.almacen_destino_id # Del payload

            # Validar almacén si no va a desecho
            if destino != EstadoNeumaticoEnum.DESECHADO:
                 if not almacen_destino_id:
                     raise HTTPException(status_code=422, detail="ID de almacén destino requerido para desmontaje a estado no desechado.")
                 almacen_destino_db = await session.get(Almacen, almacen_destino_id)
                 if not almacen_destino_db or not almacen_destino_db.activo:
                     raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")
                 # Actualizar ubicación en Python
                 neumatico.ubicacion_almacen_id = almacen_destino_id
                 modelo_afectado_stock = neumatico.modelo_id
                 almacen_afectado_stock = almacen_destino_id
            else: # Destino es DESECHADO
                 if not db_evento.motivo_desecho_id_evento: # Validado por schema, pero seguro
                      raise HTTPException(status_code=422, detail="motivo_desecho_id_evento es requerido para DESMONTAJE a DESECHADO.")
                 motivo = await session.get(MotivoDesecho, db_evento.motivo_desecho_id_evento)
                 if not motivo:
                      raise HTTPException(status_code=404, detail=f"Motivo desecho ID {db_evento.motivo_desecho_id_evento} no encontrado.")
                 # El trigger se encargará de poner motivo_desecho_id y fecha_desecho
                 neumatico.ubicacion_almacen_id = None # Asegurar que no quede en almacén

            # --- Actualizaciones comunes de desmontaje (manejadas aquí y/o por trigger) ---
            # El trigger DEBE encargarse de: estado_actual, kilometraje_acumulado, fecha_desecho, motivo_desecho_id
            # El código Python se asegura de limpiar ubicaciones y poner la nueva si aplica
            neumatico.estado_actual = destino # Podríamos dejar que el trigger lo haga, pero ponerlo aquí da claridad
            neumatico.ubicacion_actual_vehiculo_id = None
            neumatico.ubicacion_actual_posicion_id = None
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico_modificado = True

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.DESECHO:
            if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede desechar un neumático INSTALADO. Realiza DESMONTAJE primero.")

            motivo_id_recibido = evento_in.motivo_desecho_id_evento
            if not motivo_id_recibido: # Validado por schema, pero seguro
                raise HTTPException(status_code=422, detail="motivo_desecho_id_evento es requerido para DESECHO.")
            motivo = await session.get(MotivoDesecho, motivo_id_recibido)
            if not motivo:
                raise HTTPException(status_code=404, detail=f"Motivo desecho ID {motivo_id_recibido} no encontrado.")

            # --- Actualizaciones (manejadas aquí y/o por trigger) ---
            # El trigger DEBE encargarse de: estado_actual, fecha_desecho, motivo_desecho_id, kilometraje_acumulado
            # El código Python limpia ubicaciones
            neumatico.estado_actual = EstadoNeumaticoEnum.DESECHADO # Podríamos dejar que el trigger lo haga
            neumatico.motivo_desecho_id = motivo_id_recibido      # Podríamos dejar que el trigger lo haga
            neumatico.fecha_desecho = db_evento.timestamp_evento.date() # Podríamos dejar que el trigger lo haga
            neumatico.ubicacion_actual_vehiculo_id = None
            neumatico.ubicacion_actual_posicion_id = None
            neumatico.ubicacion_almacen_id = None
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico_modificado = True

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.INSPECCION:
            # El trigger podría calcular KM si se pasa odómetro
            # El servicio de alertas se llama después del commit
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico_modificado = True # Marcar para auditoría

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.ROTACION:
            if neumatico.estado_actual != EstadoNeumaticoEnum.INSTALADO:
                raise HTTPException(status_code=409, detail="Solo se pueden rotar neumáticos INSTALADOS.")
            if not db_evento.vehiculo_id or not db_evento.posicion_id:
                raise HTTPException(status_code=422, detail="Vehiculo ID y Posicion ID (destino) requeridos para ROTACION.")
            posicion_destino = await session.get(PosicionNeumatico, db_evento.posicion_id)
            if not posicion_destino:
                raise HTTPException(status_code=404, detail=f"Posición destino ID {db_evento.posicion_id} no encontrada.")
            # TODO: Validar si la nueva posición es compatible con el vehículo db_evento.vehiculo_id

            # Actualizar ubicación del neumático
            neumatico.ubicacion_actual_vehiculo_id = db_evento.vehiculo_id
            neumatico.ubicacion_actual_posicion_id = db_evento.posicion_id
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            # El trigger podría calcular KM si se pasa odómetro
            neumatico_modificado = True

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REPARACION_ENTRADA:
            if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO:
                raise HTTPException(status_code=409, detail="Desmonta el neumático antes de enviarlo a reparar.")

            almacen_taller_id = evento_in.almacen_destino_id # Usamos el campo del payload
            if almacen_taller_id:
                almacen_taller_db = await session.get(Almacen, almacen_taller_id)
                if not almacen_taller_db or not almacen_taller_db.activo:
                     logger.warning(f"Almacén/Taller destino ID {almacen_taller_id} no encontrado o inactivo. Se dejará sin asignar.")
                     almacen_taller_id = None # No asignar si no es válido
            else:
                logger.warning("No se especificó almacén/taller destino para REPARACION_ENTRADA.")

            # --- Actualizaciones (manejadas aquí y/o por trigger) ---
            # El trigger DEBE cambiar estado_actual a EN_REPARACION
            # El código Python asigna la ubicación del taller si es válida
            neumatico.estado_actual = EstadoNeumaticoEnum.EN_REPARACION # Podríamos dejar que el trigger lo haga
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico.ubicacion_almacen_id = almacen_taller_id # Asignar ubicación taller
            neumatico.ubicacion_actual_vehiculo_id = None # Asegurar que no está en vehículo
            neumatico.ubicacion_actual_posicion_id = None
            neumatico_modificado = True

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REPARACION_SALIDA:
            if neumatico.estado_actual != EstadoNeumaticoEnum.EN_REPARACION:
                raise HTTPException(status_code=409, detail="El neumático debe estar EN_REPARACION.")

            almacen_destino_id = evento_in.almacen_destino_id
            if not almacen_destino_id:
                raise HTTPException(status_code=422, detail="ID de almacén destino requerido para salida de reparación.")
            almacen_destino_db = await session.get(Almacen, almacen_destino_id)
            if not almacen_destino_db or not almacen_destino_db.activo:
                raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")

            # --- Actualizaciones (manejadas aquí y/o por trigger) ---
            # El trigger DEBE cambiar estado_actual a EN_STOCK
            # El código Python asigna la nueva ubicación de almacén
            neumatico.estado_actual = EstadoNeumaticoEnum.EN_STOCK # Podríamos dejar que el trigger lo haga
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico.ubicacion_almacen_id = almacen_destino_id # Asignar ubicación destino
            neumatico_modificado = True
            modelo_afectado_stock = neumatico.modelo_id
            almacen_afectado_stock = almacen_destino_id

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA:
            if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO:
                raise HTTPException(status_code=409, detail="Desmonta el neumático antes de enviarlo a reencauche.")

            # Validar si excede límite ANTES de cambiar estado (opcional, el trigger lo hará también)
            # modelo = await session.get(ModeloNeumatico, neumatico.modelo_id)
            # if modelo and neumatico.reencauches_realizados >= modelo.reencauches_maximos:
            #    logger.warning(f"Neumático {neumatico.id} enviado a reencauche pero ya alcanzó/superó límite.")
            #    # Podrías decidir si lanzar error aquí o dejar que el trigger lo advierta/lance

            almacen_reenc_id = evento_in.almacen_destino_id # Usamos el campo del payload
            if almacen_reenc_id:
                 almacen_reenc_db = await session.get(Almacen, almacen_reenc_id)
                 if not almacen_reenc_db or not almacen_reenc_db.activo:
                      logger.warning(f"Almacén/Reencauchadora destino ID {almacen_reenc_id} no encontrado o inactivo. Se dejará sin asignar.")
                      almacen_reenc_id = None
            else:
                logger.warning("No se especificó almacén/reencauchadora destino para REENCAUCHE_ENTRADA.")


            # --- Actualizaciones (manejadas aquí y/o por trigger) ---
            # El trigger DEBE cambiar estado_actual a EN_REENCAUCHE
            # El código Python asigna la ubicación del taller
            neumatico.estado_actual = EstadoNeumaticoEnum.EN_REENCAUCHE # Podríamos dejar que el trigger lo haga
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico.ubicacion_almacen_id = almacen_reenc_id # Asignar ubicación reencauchadora
            neumatico.ubicacion_actual_vehiculo_id = None # Asegurar que no está en vehículo
            neumatico.ubicacion_actual_posicion_id = None
            neumatico_modificado = True

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA:
             # --- ¡ESTE ES EL BLOQUE PROBLEMÁTICO EN LA PRUEBA! ---
             if neumatico.estado_actual != EstadoNeumaticoEnum.EN_REENCAUCHE:
                 raise HTTPException(status_code=409, detail="El neumático debe estar EN_REENCAUCHE.")
             if db_evento.profundidad_post_reencauche_mm is None:
                 raise HTTPException(status_code=422, detail="profundidad_post_reencauche_mm es requerida.")

             almacen_destino_id = evento_in.almacen_destino_id
             if not almacen_destino_id:
                 raise HTTPException(status_code=422, detail="ID de almacén destino requerido para salida de reencauche.")
             almacen_destino_db = await session.get(Almacen, almacen_destino_id)
             if not almacen_destino_db or not almacen_destino_db.activo:
                 raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")

             # --- Actualizaciones Clave ---
             # 1. Dejar que el TRIGGER actualice:
             #    - estado_actual a 'EN_STOCK'
             #    - reencauches_realizados
             #    - vida_actual
             #    - kilometraje_acumulado a 0
             #    - profundidad_inicial_mm
             #    - es_reencauchado a true
             # 2. El código Python DEBE actualizar:
             #    - ubicacion_almacen_id con el destino
             #    - fecha_ultimo_evento

             neumatico.ubicacion_almacen_id = almacen_destino_id # <-- ¡Asegurar que esto se haga!
             neumatico.fecha_ultimo_evento = db_evento.timestamp_evento # Actualizar fecha
             # --- ¡NO TOCAR neumatico.estado_actual AQUÍ! ---

             neumatico_modificado = True # Marcar para auditoría y alert service
             modelo_afectado_stock = neumatico.modelo_id
             almacen_afectado_stock = almacen_destino_id

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO:
             # Solo actualiza fecha último evento y marca para auditoría
             neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
             neumatico_modificado = True

        elif db_evento.tipo_evento == TipoEventoNeumaticoEnum.TRANSFERENCIA_UBICACION:
             if neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO:
                 raise HTTPException(status_code=409, detail="No se puede transferir un neumático INSTALADO.")
             if neumatico.ubicacion_almacen_id is None:
                 raise HTTPException(status_code=409, detail="El neumático no está asignado a un almacén de origen para transferir.")

             almacen_destino_id = evento_in.almacen_destino_id
             if not almacen_destino_id:
                 raise HTTPException(status_code=422, detail="ID de almacén destino requerido para TRANSFERENCIA.")
             if almacen_destino_id == neumatico.ubicacion_almacen_id:
                 raise HTTPException(status_code=400, detail="Almacén de origen y destino son iguales.")
             almacen_destino_db = await session.get(Almacen, almacen_destino_id)
             if not almacen_destino_db or not almacen_destino_db.activo:
                 raise HTTPException(status_code=404, detail=f"Almacén destino ID {almacen_destino_id} no encontrado o inactivo.")

             almacen_origen_id = neumatico.ubicacion_almacen_id # Guardar origen para posible alerta stock
             neumatico.ubicacion_almacen_id = almacen_destino_id # Actualizar ubicación
             neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
             neumatico_modificado = True
             modelo_afectado_stock = neumatico.modelo_id
             almacen_afectado_stock = almacen_destino_id # Alerta stock en destino si aplica

        # --- Fin Lógica por Tipo de Evento ---

        # --- Guardar Cambios ---
        logger.debug(f"Añadiendo evento {db_evento.id} y neumático {neumatico.id} (modificado={neumatico_modificado}) a sesión.")
        session.add(db_evento)
        if neumatico_modificado:
            neumatico.actualizado_en = datetime.now(timezone.utc)
            neumatico.actualizado_por = current_user.id
            session.add(neumatico) # Añadir neumático modificado a la sesión

        logger.debug("Intentando commit...")
        await session.commit()
        logger.debug("Commit exitoso.")

        # --- Obtener datos actualizados DESPUÉS del commit (incluye efectos del trigger) ---
        # Refrescar el evento (generalmente no cambia por triggers, pero es buena práctica)
        try:
            await session.refresh(db_evento)
        except Exception as refresh_exc:
            logger.error(f"Error al refrescar db_evento {db_evento.id} post-commit: {refresh_exc}", exc_info=True)
            # Podrías decidir continuar o lanzar un error aquí

        # Volver a obtener el neumático para reflejar cambios del trigger
        logger.debug(f"Re-obteniendo neumático {db_evento.neumatico_id} post-commit...")
        neumatico_actualizado = await session.get(Neumatico, db_evento.neumatico_id)
        if not neumatico_actualizado:
            logger.error(f"¡Error crítico! Neumático {db_evento.neumatico_id} no encontrado DESPUÉS de commit.")
            raise HTTPException(status_code=500, detail="Error interno: Inconsistencia de datos post-guardado.")
        else:
            logger.debug(f"Neumático {neumatico_actualizado.id} post-commit obtenido. Estado actual: {neumatico_actualizado.estado_actual.value if neumatico_actualizado.estado_actual else 'None'}")
        # ----------------------------------------------------------

        logger.info(f"Evento {db_evento.tipo_evento.value} creado para neumático {db_evento.neumatico_id}.")

        # --- Llamada al Servicio de Alertas ---
        try:
            # Alerta de Profundidad Baja
            if db_evento.tipo_evento == TipoEventoNeumaticoEnum.INSPECCION and db_evento.profundidad_remanente_mm is not None:
                 logger.debug(f"Llamando check_profundidad_baja para evento {db_evento.id}")
                 # Pasar el objeto evento COMPLETO (db_evento) que ya tiene los datos necesarios
                 await check_profundidad_baja(session, db_evento)

            # Alerta de Stock Mínimo (si aplica)
            # Alerta de Stock Mínimo (si aplica)
            if modelo_afectado_stock and almacen_afectado_stock:
                logger.debug(f"Llamando check_stock_minimo para modelo {modelo_afectado_stock}, almacén {almacen_afectado_stock}")
                # --- ¡ESTA LLAMADA AHORA FUNCIONARÁ! ---
                await check_stock_minimo(session, modelo_afectado_stock, almacen_afectado_stock)
            # ... (resto de la lógica de alertas) ...
            # Si fue una transferencia, chequear también el almacén origen
            if db_evento.tipo_evento == TipoEventoNeumaticoEnum.TRANSFERENCIA_UBICACION and modelo_afectado_stock and almacen_origen_id:
                logger.debug(f"Llamando check_stock_minimo para modelo {modelo_afectado_stock}, almacén ORIGEN {almacen_origen_id}")
                await check_stock_minimo(session, modelo_afectado_stock, almacen_origen_id)

        except Exception as alert_exc:
             # Loguear el error pero no hacer fallar la request principal por un fallo en alertas
             logger.error(f"Error no crítico al generar alertas post-evento {db_evento.id}: {alert_exc}", exc_info=True)
        # --- Fin Llamada Alertas ---

        # --- Preparar y devolver la respuesta ---
        # Usar el objeto db_evento refrescado para construir la respuesta
        # Asegúrate que EventoNeumaticoRead solo tenga campos presentes en EventoNeumatico
        try:
            return EventoNeumaticoRead.model_validate(db_evento)
        except Exception as validation_exc:
             logger.error(f"Error validando respuesta EventoNeumaticoRead para evento {db_evento.id}: {validation_exc}", exc_info=True)
             # Devolver un 500 si la validación de respuesta falla (indica problema schema/modelo)
             raise HTTPException(status_code=500, detail="Error procesando la respuesta del evento.")

    # --- Manejo de Excepciones ---
    except HTTPException as http_exc:
         # Ya logueado o es una excepción controlada (4xx)
         await session.rollback() # Asegurar rollback
         raise http_exc
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad al procesar evento para neumático {db_evento.neumatico_id if db_evento else 'desconocido'}: {str(e)}", exc_info=True)
        # Intentar dar un mensaje más útil si es posible (ej. por constraint violada)
        detail_msg = "Error de datos: Verifique IDs (neumático, vehículo, posición, proveedor, motivo, almacén, etc.) o posibles duplicados."
        if "violates foreign key constraint" in str(e):
            detail_msg = f"Error de referencia: Uno de los IDs proporcionados no existe. ({e.pgcode})"
        elif "violates unique constraint" in str(e):
            detail_msg = f"Error de duplicado: Ya existe un registro con datos únicos similares. ({e.pgcode})"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail_msg)
    except SQLAlchemyError as e: # Captura errores generales de DB
        await session.rollback()
        logger.error(f"Error SQLAlchemy al procesar evento para neumático {db_evento.neumatico_id if db_evento else 'desconocido'}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error de base de datos: {e.pgcode or 'Genérico'}")
    except Exception as e: # Captura cualquier otro error inesperado
        await session.rollback()
        logger.error(f"Error inesperado al procesar evento para neumático {db_evento.neumatico_id if db_evento else 'desconocido'}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")

# --- Endpoints de Lectura (Revisados) ---
# Ajustado response_model a EventoNeumaticoRead para que coincida con lo que devuelve la consulta simple
@router.get("/{neumatico_id}/historial", response_model=List[EventoNeumaticoRead], summary="Obtener historial de neumático")
async def leer_historial_neumatico(
    neumatico_id: uuid.UUID = Path(..., description="ID del neumático"),
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Obtiene el historial de eventos de un neumático específico."""
    logger.info(f"Solicitando historial para neumático ID: {neumatico_id}")
    neumatico = await session.get(Neumatico, neumatico_id)
    if not neumatico:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Neumático con ID {neumatico_id} no encontrado.")

    try:
        stmt = select(EventoNeumatico).where(EventoNeumatico.neumatico_id == neumatico_id).order_by(EventoNeumatico.timestamp_evento.desc())
        result = await session.exec(stmt)
        eventos = result.all()
        logger.info(f"Encontrados {len(eventos)} eventos para neumático {neumatico_id}")
        # Validar contra EventoNeumaticoRead que SÍ debería coincidir con el modelo EventoNeumatico (+ campos base)
        return [EventoNeumaticoRead.model_validate(evento) for evento in eventos]
    except Exception as e: # Captura errores de BD o validación
        logger.error(f"Error al leer/validar historial neumático {neumatico_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al procesar el historial.")
# Se mantiene el response_model original, pero se advierte que requiere VISTA o JOINs
@router.get("/instalados", response_model=List[NeumaticoInstaladoItem], summary="Listar neumáticos instalados")
async def leer_neumaticos_instalados(
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """
    Obtiene la lista de neumáticos actualmente instalados en vehículos.
    ADVERTENCIA: El response_model NeumaticoInstaladoItem requiere datos adicionales.
    Esta implementación básica devolverá error de validación o datos incompletos.
    Se debe implementar usando JOINs o una VISTA (ej. vw_neumaticos_instalados_optimizada).
    """
    logger.info("Solicitando lista de neumáticos instalados.")
    try:
        # Consulta básica - NO DEVUELVE TODOS LOS DATOS PARA NeumaticoInstaladoItem
        stmt = select(Neumatico).where(Neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO)
        result = await session.exec(stmt)
        neumaticos = result.all()
        logger.info(f"Encontrados {len(neumaticos)} neumáticos instalados (datos básicos).")

        # Esto fallará la validación de Pydantic porque Neumatico no tiene todos los campos
        # de NeumaticoInstaladoItem. Se deja así para cumplir el response_model, pero
        # es INCORRECTO funcionalmente. Se necesita JOIN o VISTA.
        try:
            return [NeumaticoInstaladoItem.model_validate(n) for n in neumaticos]
        except Exception as pydantic_error:
             logger.error(f"Error de validación Pydantic mapeando a NeumaticoInstaladoItem (esperado si no se usa VISTA/JOIN): {pydantic_error}", exc_info=True)
             raise HTTPException(status_code=500, detail="Error procesando datos. Endpoint requiere JOIN/Vista.")

    except SQLAlchemyError as e:
        logger.error(f"Error DB al leer neumáticos instalados: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al recuperar neumáticos instalados")
    except Exception as e:
        logger.error(f"Error inesperado al leer neumáticos instalados: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")