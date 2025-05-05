# services/neumatico_service.py
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession # Usar AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound # Importar excepciones específicas
from sqlalchemy.orm import selectinload

# --- Modelos y Schemas necesarios ---
from models.neumatico import Neumatico
from models.evento_neumatico import EventoNeumatico
from models.almacen import Almacen
from models.motivo_desecho import MotivoDesecho
from models.usuario import Usuario # Para tipo de usuario
from models.vehiculo import Vehiculo # Necesario para obtener odómetro previo? (Opcional)
from models.posicion_neumatico import PosicionNeumatico # Necesario para validación ROTACION
from schemas.evento_neumatico import EventoNeumaticoCreate # Schema de entrada
from schemas.common import EstadoNeumaticoEnum, TipoEventoNeumaticoEnum

logger = logging.getLogger(__name__)

# --- Clases de Excepciones Personalizadas para el Servicio ---
class ServiceError(Exception):
    """Clase base para excepciones de la capa de servicio."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NeumaticoNotFoundError(ServiceError):
    """Excepción cuando no se encuentra el neumático."""
    def __init__(self, neumatico_id: uuid.UUID):
        super().__init__(f"Neumático ID {neumatico_id} no encontrado.", status_code=404)

class ValidationError(ServiceError):
    """Excepción para errores de validación de datos o reglas de negocio."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422) # 422 Unprocessable Entity

class ConflictError(ServiceError):
    """Excepción para conflictos de estado."""
    def __init__(self, message: str):
        super().__init__(message, status_code=409) # 409 Conflict


class NeumaticoService:
    """
    Encapsula la lógica de negocio relacionada con neumáticos y sus eventos.
    """

    async def _get_ultimo_odometro_instalacion(
        self, neumatico_id: uuid.UUID, db: AsyncSession
    ) -> Optional[int]:
        """Helper para obtener el odómetro del último evento de instalación."""
        stmt_install = select(EventoNeumatico).where(
            EventoNeumatico.neumatico_id == neumatico_id,
            EventoNeumatico.tipo_evento == TipoEventoNeumaticoEnum.INSTALACION
        ).order_by(EventoNeumatico.timestamp_evento.desc()).limit(1)
        # Usamos await db.exec() con SQLModel/SQLAlchemy 2.0+
        result = await db.exec(stmt_install)
        last_install_event = result.first()
        if last_install_event and last_install_event.odometro_vehiculo_en_evento is not None:
            return last_install_event.odometro_vehiculo_en_evento
        logger.warning(f"Servicio: No se encontró evento de instalación o su odómetro para neumático {neumatico_id}")
        return None

    async def crear_evento_y_actualizar_neumatico(
        self,
        evento_in: EventoNeumaticoCreate,
        current_user: Usuario,
        db: AsyncSession
    ) -> Tuple[EventoNeumatico, Optional[uuid.UUID], Optional[uuid.UUID]]:
        """
        Crea un EventoNeumatico y actualiza el Neumatico asociado en la misma sesión.
        NO HACE COMMIT. Lanza excepciones del servicio en caso de error.
        Devuelve: El objeto EventoNeumatico creado (sin commit),
                 ID del almacén de salida (si aplica), ID del almacén de entrada (si aplica).
        """
        logger.info(f"Servicio: Procesando evento {evento_in.tipo_evento.value} para neumático ID {evento_in.neumatico_id}")

        # 1. Obtener neumático
        neumatico = await db.get(Neumatico, evento_in.neumatico_id)
        if not neumatico:
            raise NeumaticoNotFoundError(evento_in.neumatico_id)

        logger.debug(f"Servicio: Neumático {neumatico.id} encontrado. Estado ANTES: {neumatico.estado_actual.value if neumatico.estado_actual else 'None'}")
        estado_original = neumatico.estado_actual
        nuevo_estado_asignado: Optional[EstadoNeumaticoEnum] = None
        neumatico_modificado = False

        # Variables del payload
        vehiculo_id_evento = evento_in.vehiculo_id
        posicion_id_evento = evento_in.posicion_id
        destino_desmontaje_evento = evento_in.destino_desmontaje
        almacen_destino_id_evento = evento_in.almacen_destino_id
        motivo_desecho_id_evento = evento_in.motivo_desecho_id_evento
        odometro_evento = evento_in.odometro_vehiculo_en_evento
        profundidad_post_reencauche = evento_in.profundidad_post_reencauche_mm

        # Variables para seguimiento de stock (para alertas post-commit)
        almacen_afectado_stock_entrada: Optional[uuid.UUID] = None
        almacen_afectado_stock_salida: Optional[uuid.UUID] = neumatico.ubicacion_almacen_id # El almacén actual es potencial salida

        # 2. Crear instancia base del evento (se añadirá al final)
        evento_data = evento_in.model_dump(exclude_unset=True)
        evento_data['usuario_id'] = current_user.id 
        evento_data['timestamp_evento'] = datetime.now(timezone.utc)
        db_evento = EventoNeumatico.model_validate(evento_data)
        db_evento.usuario_id = current_user.id
        db_evento.timestamp_evento = datetime.now(timezone.utc)

        # 3. Lógica principal por tipo de evento
        match evento_in.tipo_evento:
            case TipoEventoNeumaticoEnum.INSTALACION:
                if not vehiculo_id_evento or not posicion_id_evento:
                    raise ValidationError("Vehiculo ID y Posicion ID requeridos para INSTALACION.")
                if estado_original != EstadoNeumaticoEnum.EN_STOCK:
                    raise ConflictError(f"Neumático debe estar EN_STOCK (estado actual: {estado_original.value if estado_original else 'None'}).")
                # TODO: Validar si la posición está ocupada, vehículo existe/activo, compatibilidad, etc. (RF16)
                logger.debug("Servicio: Validaciones de instalación OK (simplificado).")

                nuevo_estado_asignado = EstadoNeumaticoEnum.INSTALADO
                neumatico.ubicacion_actual_vehiculo_id = vehiculo_id_evento
                neumatico.ubicacion_actual_posicion_id = posicion_id_evento
                neumatico.ubicacion_almacen_id = None # Sale del almacén
                neumatico.kilometraje_acumulado = 0

            case TipoEventoNeumaticoEnum.DESMONTAJE:
                if estado_original != EstadoNeumaticoEnum.INSTALADO:
                    raise ConflictError("Solo se pueden desmontar neumáticos INSTALADOS.")
                if not destino_desmontaje_evento:
                    raise ValidationError("destino_desmontaje es requerido para DESMONTAJE.")
                if destino_desmontaje_evento == EstadoNeumaticoEnum.INSTALADO:
                     raise ValidationError("Destino de desmontaje no puede ser INSTALADO.")

                nuevo_estado_asignado = destino_desmontaje_evento

                if nuevo_estado_asignado != EstadoNeumaticoEnum.DESECHADO:
                    if not almacen_destino_id_evento:
                         raise ValidationError("ID de almacén destino requerido si destino no es DESECHADO.")
                    almacen_destino_db = await db.get(Almacen, almacen_destino_id_evento)
                    if not almacen_destino_db or not almacen_destino_db.activo:
                         raise ValidationError(f"Almacén destino ID {almacen_destino_id_evento} no encontrado o inactivo.")
                    neumatico.ubicacion_almacen_id = almacen_destino_id_evento
                    almacen_afectado_stock_entrada = almacen_destino_id_evento
                    almacen_afectado_stock_salida = None # No sale de stock, entra a uno nuevo
                else: # Destino es DESECHADO
                    if not motivo_desecho_id_evento:
                         raise ValidationError("motivo_desecho_id_evento es requerido para DESMONTAJE a DESECHADO.")
                    motivo = await db.get(MotivoDesecho, motivo_desecho_id_evento)
                    if not motivo:
                         raise ValidationError(f"Motivo desecho ID {motivo_desecho_id_evento} no encontrado.")
                    neumatico.motivo_desecho_id = motivo_desecho_id_evento
                    neumatico.fecha_desecho = db_evento.timestamp_evento.date()
                    neumatico.ubicacion_almacen_id = None # No va a almacén
                    almacen_afectado_stock_entrada = None

                # Calcular KM acumulado
                if odometro_evento is not None:
                    odometro_instalacion = await self._get_ultimo_odometro_instalacion(neumatico.id, db)
                    if odometro_instalacion is not None:
                        km_recorridos = odometro_evento - odometro_instalacion
                        if km_recorridos >= 0:
                            neumatico.kilometraje_acumulado = (neumatico.kilometraje_acumulado or 0) + km_recorridos
                            logger.debug(f"Servicio: KM acumulados actualizados a: {neumatico.kilometraje_acumulado}")
                        else:
                            logger.warning(f"Servicio: Odómetro de desmontaje {odometro_evento} menor que el de instalación {odometro_instalacion}, no se actualiza KM.")

                # Limpiar ubicación vehículo/posición (siempre al desmontar)
                neumatico.ubicacion_actual_vehiculo_id = None
                neumatico.ubicacion_actual_posicion_id = None

            case TipoEventoNeumaticoEnum.DESECHO:
                if estado_original == EstadoNeumaticoEnum.INSTALADO:
                    raise ConflictError("No se puede desechar un neumático INSTALADO. Realiza DESMONTAJE primero.")
                if not motivo_desecho_id_evento:
                    raise ValidationError("motivo_desecho_id_evento es requerido para DESECHO.")
                motivo = await db.get(MotivoDesecho, motivo_desecho_id_evento)
                if not motivo:
                    raise ValidationError(f"Motivo desecho ID {motivo_desecho_id_evento} no encontrado.")

                nuevo_estado_asignado = EstadoNeumaticoEnum.DESECHADO
                neumatico.motivo_desecho_id = motivo_desecho_id_evento
                neumatico.fecha_desecho = db_evento.timestamp_evento.date()
                neumatico.ubicacion_actual_vehiculo_id = None
                neumatico.ubicacion_actual_posicion_id = None
                neumatico.ubicacion_almacen_id = None # Sale de donde estuviera
                almacen_afectado_stock_entrada = None # No entra a stock

            case TipoEventoNeumaticoEnum.ROTACION:
                if estado_original != EstadoNeumaticoEnum.INSTALADO:
                    raise ConflictError("Solo se pueden rotar neumáticos INSTALADOS.")
                if not vehiculo_id_evento or not posicion_id_evento:
                    raise ValidationError("Vehiculo ID y Posicion ID de destino requeridos para ROTACION.")
                posicion_destino = await db.get(PosicionNeumatico, posicion_id_evento)
                if not posicion_destino:
                    raise ValidationError(f"Posición destino ID {posicion_id_evento} no encontrada.")
                # TODO: Validar compatibilidad vehículo/posición

                nuevo_estado_asignado = EstadoNeumaticoEnum.INSTALADO # Estado no cambia
                neumatico.ubicacion_actual_vehiculo_id = vehiculo_id_evento
                neumatico.ubicacion_actual_posicion_id = posicion_id_evento
                almacen_afectado_stock_entrada = None # No afecta stock
                almacen_afectado_stock_salida = None

            case TipoEventoNeumaticoEnum.REPARACION_ENTRADA:
                if estado_original == EstadoNeumaticoEnum.INSTALADO:
                    raise ConflictError("Desmonta el neumático antes de enviarlo a reparar.")
                if not almacen_destino_id_evento:
                     raise ValidationError("ID de almacén/taller destino requerido para REPARACION_ENTRADA.")
                taller = await db.get(Almacen, almacen_destino_id_evento)
                if not taller: raise ValidationError(f"Taller/Almacén destino {almacen_destino_id_evento} no encontrado.")

                nuevo_estado_asignado = EstadoNeumaticoEnum.EN_REPARACION
                neumatico.ubicacion_almacen_id = almacen_destino_id_evento
                neumatico.ubicacion_actual_vehiculo_id = None
                neumatico.ubicacion_actual_posicion_id = None
                almacen_afectado_stock_entrada = None # No entra a stock usable

            case TipoEventoNeumaticoEnum.REPARACION_SALIDA:
                if estado_original != EstadoNeumaticoEnum.EN_REPARACION:
                    raise ConflictError("El neumático debe estar EN_REPARACION.")
                if not almacen_destino_id_evento:
                    raise ValidationError("ID de almacén destino requerido para REPARACION_SALIDA.")
                almacen_destino_db = await db.get(Almacen, almacen_destino_id_evento)
                if not almacen_destino_db or not almacen_destino_db.activo:
                    raise ValidationError(f"Almacén destino ID {almacen_destino_id_evento} no encontrado o inactivo.")

                nuevo_estado_asignado = EstadoNeumaticoEnum.EN_STOCK
                neumatico.ubicacion_almacen_id = almacen_destino_id_evento
                almacen_afectado_stock_entrada = almacen_destino_id_evento # Entra a stock usable
                almacen_afectado_stock_salida = None # Sale de reparación, no de stock usable

            case TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA:
                if estado_original == EstadoNeumaticoEnum.INSTALADO:
                    raise ConflictError("Desmonta el neumático antes de enviarlo a reencauche.")
                if not almacen_destino_id_evento:
                     raise ValidationError("ID de almacén/reencauchadora destino requerido para REENCAUCHE_ENTRADA.")
                reencauchadora = await db.get(Almacen, almacen_destino_id_evento)
                if not reencauchadora: raise ValidationError(f"Reencauchadora/Almacén destino {almacen_destino_id_evento} no encontrado.")

                nuevo_estado_asignado = EstadoNeumaticoEnum.EN_REENCAUCHE
                neumatico.ubicacion_almacen_id = almacen_destino_id_evento
                neumatico.ubicacion_actual_vehiculo_id = None
                neumatico.ubicacion_actual_posicion_id = None
                almacen_afectado_stock_entrada = None # No entra a stock usable

            case TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA:
                if estado_original != EstadoNeumaticoEnum.EN_REENCAUCHE:
                    raise ConflictError("El neumático debe estar EN_REENCAUCHE.")
                if profundidad_post_reencauche is None:
                    raise ValidationError("profundidad_post_reencauche_mm es requerida para REENCAUCHE_SALIDA.")
                if not almacen_destino_id_evento:
                    raise ValidationError("ID de almacén destino requerido para REENCAUCHE_SALIDA.")
                almacen_destino_db = await db.get(Almacen, almacen_destino_id_evento)
                if not almacen_destino_db or not almacen_destino_db.activo:
                    raise ValidationError(f"Almacén destino ID {almacen_destino_id_evento} no encontrado o inactivo.")

                nuevo_estado_asignado = EstadoNeumaticoEnum.EN_STOCK
                neumatico.reencauches_realizados = (neumatico.reencauches_realizados or 0) + 1
                neumatico.vida_actual = (neumatico.vida_actual or 0) + 1
                neumatico.es_reencauchado = True
                neumatico.profundidad_inicial_mm = profundidad_post_reencauche # Actualizar profundidad
                neumatico.kilometraje_acumulado = 0 # Resetear KM
                neumatico.ubicacion_almacen_id = almacen_destino_id_evento
                almacen_afectado_stock_entrada = almacen_destino_id_evento # Entra a stock usable
                almacen_afectado_stock_salida = None # Sale de reencauche, no de stock usable
                logger.info(f"Servicio: Reencauche Salida para neumático {neumatico.id}")

            case TipoEventoNeumaticoEnum.TRANSFERENCIA_UBICACION:
                if estado_original == EstadoNeumaticoEnum.INSTALADO:
                    raise ConflictError("No se puede transferir un neumático INSTALADO. Realiza DESMONTAJE.")
                if neumatico.ubicacion_almacen_id is None:
                    raise ConflictError("El neumático no está actualmente en un almacén de origen para transferir.")
                if not almacen_destino_id_evento:
                    raise ValidationError("ID de almacén destino requerido para TRANSFERENCIA.")
                if almacen_destino_id_evento == neumatico.ubicacion_almacen_id:
                    raise ValidationError("Almacén de origen y destino son iguales.")
                almacen_destino_db = await db.get(Almacen, almacen_destino_id_evento)
                if not almacen_destino_db or not almacen_destino_db.activo:
                    raise ValidationError(f"Almacén destino ID {almacen_destino_id_evento} no encontrado o inactivo.")

                # El estado no cambia (asumimos que sigue EN_STOCK, EN_REPARACION, etc.)
                nuevo_estado_asignado = estado_original
                # Se actualiza ubicación
                neumatico.ubicacion_almacen_id = almacen_destino_id_evento
                # Se registra entrada y salida para alertas
                almacen_afectado_stock_entrada = almacen_destino_id_evento
                # almacen_afectado_stock_salida ya tiene el valor original al inicio

            case TipoEventoNeumaticoEnum.COMPRA:
                logger.warning("Servicio: Evento COMPRA no debería actualizar un neumático existente vía este endpoint.")
                # No hacer cambios aquí, la compra debe crear el neumático
                pass
            case TipoEventoNeumaticoEnum.INSPECCION | TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO:
                 logger.debug(f"Servicio: Evento {evento_in.tipo_evento.value} no modifica estado/ubicación principal.")
                 # Podrías actualizar profundidad aquí si es INSPECCION
                 if evento_in.tipo_evento == TipoEventoNeumaticoEnum.INSPECCION and evento_in.profundidad_remanente_mm is not None:
                      # Aquí hay una decisión de diseño: ¿Actualizamos profundidad_inicial_mm o creamos un nuevo campo profundidad_actual_mm?
                      # Asumiendo que queremos un campo separado para la profundidad actual medida:
                      # neumatico.profundidad_actual_medida_mm = evento_in.profundidad_remanente_mm
                      # neumatico.fecha_ultima_medicion = db_evento.timestamp_evento
                      # Esto requiere añadir esos campos al modelo Neumatico
                      logger.warning("Servicio: Actualización de profundidad en INSPECCION no implementada (requiere campo adicional en modelo Neumatico).")
                      neumatico_modificado = True # Marcar como modificado si actualizas algo
                 pass
            case _:
                logger.warning(f"Servicio: Tipo de evento {evento_in.tipo_evento.value} no manejado explícitamente.")
                pass

        # 4. Aplicar cambios finales al neumático
        if nuevo_estado_asignado is not None and neumatico.estado_actual != nuevo_estado_asignado:
            logger.info(f"Servicio: Cambiando estado neumático {neumatico.id} de {estado_original.value if estado_original else 'None'} a {nuevo_estado_asignado.value}")
            neumatico.estado_actual = nuevo_estado_asignado
            neumatico_modificado = True

        # Si hubo alguna modificación, actualizar timestamp
        if neumatico_modificado:
            # Siempre actualizar fecha_ultimo_evento si procesamos lógicamente el evento
            neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
            neumatico.actualizado_en = db_evento.timestamp_evento # Usar timestamp del evento
            neumatico.actualizado_por = current_user.id
            logger.info(f"Servicio: Neumático {neumatico.id} modificado. Nuevo estado: {neumatico.estado_actual.value if neumatico.estado_actual else 'None'}")
        else:
            # Aunque no haya modificación de estado/ubicación principal,
            # el evento ocurrió, así que actualizamos fecha_ultimo_evento.
            # No actualizamos 'actualizado_en'/'actualizado_por' si no hubo cambios lógicos en el neumático.
             if neumatico.fecha_ultimo_evento != db_evento.timestamp_evento:
                 neumatico.fecha_ultimo_evento = db_evento.timestamp_evento
                 neumatico_modificado = True # Considerar si actualizar fecha_ultimo_evento cuenta como modificación auditable
                 # Si cuenta, también actualizar 'actualizado_en' y 'actualizado_por'
                 neumatico.actualizado_en = db_evento.timestamp_evento
                 neumatico.actualizado_por = current_user.id


        # 5. Añadir objetos a la sesión
        db.add(db_evento)
        if neumatico_modificado:
            db.add(neumatico) # Añadir explícitamente si fue modificado

        logger.debug(f"Servicio: Evento y Neumático (si aplica) añadidos a la sesión para neumático {neumatico.id}.")

        # 6. Devolver el evento creado y los almacenes afectados
        return db_evento, almacen_afectado_stock_salida, almacen_afectado_stock_entrada

    # --- Otros métodos potenciales del servicio ---
    # async def obtener_historial(...)
    # async def obtener_instalados(...)
    # async def crear_neumatico(...)