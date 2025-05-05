# services/neumatico_service.py (Completo - v9 Diagnóstico)

import logging
from datetime import date, datetime, timezone
from typing import Optional, Tuple, cast
from uuid import UUID
from decimal import Decimal

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# --- Modelos y Schemas ---
from models.evento_neumatico import EventoNeumatico, TipoEventoNeumaticoEnum
from models.neumatico import EstadoNeumaticoEnum, Neumatico
from models.posicion_neumatico import PosicionNeumatico
from models.vehiculo import Vehiculo
from models.almacen import Almacen
from models.motivo_desecho import MotivoDesecho
from models.usuario import Usuario
from models.proveedor import Proveedor
from models.modelo import ModeloNeumatico
from models.configuracion_eje import ConfiguracionEje
from models.tipo_vehiculo import TipoVehiculo
from schemas.evento_neumatico import EventoNeumaticoCreate
from services.alert_service import AlertService

logger = logging.getLogger(__name__)

# --- Excepciones ---
class ServiceError(Exception):
    def __init__(self, message="Error en el servicio"): self.message = message; super().__init__(self.message)
class NeumaticoNotFoundError(ServiceError):
    def __init__(self, message="Neumático no encontrado"): super().__init__(message)
class ValidationError(ServiceError):
    def __init__(self, message="Error de validación"): super().__init__(message)
class ConflictError(ServiceError):
    def __init__(self, message="Conflicto detectado"): super().__init__(message)
# --- Fin Excepciones ---

class NeumaticoService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.alert_service = AlertService(session)

    # ... (_get..., _validate..., _check_posicion_ocupada sin cambios desde v7) ...
    async def _get_neumatico_by_id(self, neumatico_id: UUID) -> Optional[Neumatico]:
        return await self.session.get(Neumatico, neumatico_id)

    async def _get_neumatico_by_serie(self, numero_serie: str) -> Optional[Neumatico]:
        statement = select(Neumatico).where(Neumatico.numero_serie == numero_serie)
        return (await self.session.exec(statement)).first()

    async def _get_neumatico_for_update(self, neumatico_id: UUID) -> Neumatico:
        result = await self.session.get(Neumatico, neumatico_id, with_for_update=True)
        if not result: raise NeumaticoNotFoundError(f"Neumático con ID {neumatico_id} no encontrado.")
        return result

    async def _validate_and_get_almacen(self, almacen_id: Optional[UUID], required: bool = True) -> Optional[Almacen]:
        if required and not almacen_id: raise ValidationError("ID de Almacén es requerido.")
        if not almacen_id: return None
        almacen = await self.session.get(Almacen, almacen_id)
        if not almacen: raise ValidationError(f"Almacén con ID {almacen_id} no encontrado.")
        if not almacen.activo: raise ValidationError(f"Almacén con ID {almacen_id} no está activo.")
        return almacen

    async def _validate_and_get_proveedor(self, proveedor_id: Optional[UUID], required: bool = True) -> Optional[Proveedor]:
        if required and not proveedor_id: raise ValidationError("ID de Proveedor es requerido.")
        if not proveedor_id: return None
        proveedor = await self.session.get(Proveedor, proveedor_id)
        if not proveedor: raise ValidationError(f"Proveedor con ID {proveedor_id} no encontrado.")
        if not proveedor.activo: raise ValidationError(f"Proveedor con ID {proveedor_id} no está activo.")
        return proveedor




    async def _validate_and_get_vehiculo_posicion(self, event_data: EventoNeumaticoCreate) -> Tuple[Vehiculo, PosicionNeumatico]:
        """Valida y obtiene vehículo y posición activos, y verifica relación (CORREGIDO v10)."""
        if not event_data.vehiculo_id or not event_data.posicion_id:
            raise ValidationError("vehiculo_id y posicion_id requeridos.")

        vehiculo = await self.session.get(Vehiculo, event_data.vehiculo_id)
        if not vehiculo: raise ValidationError(f"Vehículo ID {event_data.vehiculo_id} no encontrado.")
        if not vehiculo.activo: raise ValidationError(f"Vehículo ID {event_data.vehiculo_id} inactivo.")

        posicion = await self.session.get(PosicionNeumatico, event_data.posicion_id)
        if not posicion: raise ValidationError(f"Posición ID {event_data.posicion_id} no encontrada.")

        # --- Inicio Corrección: Quitar refresh y cargar config_eje con session.get ---
        # Ya no se usa refresh aquí para las relaciones

        # Validar si la posición pertenece al tipo de vehículo (comparando IDs)
        if posicion.configuracion_eje_id and vehiculo.tipo_vehiculo_id:
            # Obtener explícitamente el objeto ConfiguracionEje usando su ID
            config_eje = await self.session.get(ConfiguracionEje, posicion.configuracion_eje_id)
            if not config_eje:
                # Error si el ID existe en 'posicion' pero el Eje no (problema de integridad)
                logger.error(f"Error Crítico: ConfiguracionEje ID {posicion.configuracion_eje_id} no encontrado, referenciado por Posicion {posicion.id}")
                raise ServiceError(f"No se pudo encontrar la configuración del eje para la posición {posicion.id}.")

            # Ahora sí, comparar el tipo_vehiculo_id del eje con el del vehículo
            if config_eje.tipo_vehiculo_id != vehiculo.tipo_vehiculo_id:
                logger.error(f"Discrepancia Tipo Vehículo: Vehiculo {vehiculo.id}({vehiculo.tipo_vehiculo_id}) vs Posicion {posicion.id} en Eje {posicion.configuracion_eje_id}({config_eje.tipo_vehiculo_id})")
                raise ValidationError(f"La posición {posicion.id} ({posicion.codigo_posicion}) no pertenece al tipo de vehículo del vehículo {vehiculo.numero_economico} (Tipo ID: {vehiculo.tipo_vehiculo_id}).")
        # --- Fin Corrección ---
        elif not posicion.configuracion_eje_id:
             logger.warning(f"Posición {posicion.id} ({posicion.codigo_posicion}) no tiene configuracion_eje_id asignado.")
             # Considerar si esto debe ser un ValidationError

        # Si todo está bien, devolver los objetos obtenidos
        return vehiculo, posicion


    async def _check_posicion_ocupada(self, vehiculo_id: UUID, posicion_id: UUID, current_neumatico_id: Optional[UUID] = None):
        statement = select(Neumatico.id).where(Neumatico.ubicacion_actual_vehiculo_id == vehiculo_id, Neumatico.ubicacion_actual_posicion_id == posicion_id, Neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO)
        if current_neumatico_id: statement = statement.where(Neumatico.id != current_neumatico_id)
        ocupante_id = await self.session.scalar(statement) # Usar session.scalar()
        if ocupante_id: raise ConflictError(f"Posición {posicion_id} en vehículo {vehiculo_id} ocupada por neumático {ocupante_id}.")

    async def _handle_compra(self, event_data: EventoNeumaticoCreate, current_user: Usuario) -> Neumatico:
        logger.info(f"Procesando evento COMPRA para serie {event_data.numero_serie}")
        if not event_data.numero_serie: raise ValidationError("numero_serie requerido.")
        if not event_data.modelo_id: raise ValidationError("modelo_id requerido.")
        if event_data.costo_compra is None: raise ValidationError("costo_compra requerido.")
        if not event_data.proveedor_compra_id: raise ValidationError("proveedor_compra_id requerido.")
        if not event_data.destino_almacen_id: raise ValidationError("destino_almacen_id requerido.")
        await self._validate_and_get_proveedor(event_data.proveedor_compra_id)
        almacen_destino = await self._validate_and_get_almacen(event_data.destino_almacen_id)
        modelo = await self.session.get(ModeloNeumatico, event_data.modelo_id)
        if not modelo: raise ValidationError(f"Modelo ID {event_data.modelo_id} no encontrado.")
        if await self._get_neumatico_by_serie(event_data.numero_serie):
            raise ConflictError(f"Neumático serie {event_data.numero_serie} ya existe.")
        fecha_compra_real = event_data.fecha_compra or getattr(event_data, 'fecha_evento', None) or date.today()
        new_neumatico = Neumatico(
            numero_serie=event_data.numero_serie, modelo_id=event_data.modelo_id,
            fecha_compra=fecha_compra_real, costo_compra=event_data.costo_compra,
            proveedor_compra_id=event_data.proveedor_compra_id, estado_actual=EstadoNeumaticoEnum.EN_STOCK,
            ubicacion_almacen_id=almacen_destino.id, # type: ignore
            # --- CORRECCIÓN AQUÍ ---
            kilometraje_acumulado=0, # Usar el nombre correcto del modelo
            # -----------------------
            reencauches_realizados=0, es_reencauchado=False, creado_por=current_user.id,
            profundidad_inicial_mm=modelo.profundidad_original_mm
            # Asegúrate que los campos km_instalacion y fecha_instalacion NO se inicializan aquí
        )
        self.session.add(new_neumatico); await self.session.flush(); await self.session.refresh(new_neumatico)
        logger.info(f"Neumático {new_neumatico.id} creado por evento COMPRA.")
        return new_neumatico


    async def registrar_evento(self, evento_in: EventoNeumaticoCreate, current_user: Usuario) -> Tuple[Neumatico, EventoNeumatico]:
        # ... (sin cambios en la estructura principal) ...
        tipo_evento = evento_in.tipo_evento
        event_data_dict = evento_in.model_dump(exclude_unset=True)
        timestamp_evento = datetime.now(timezone.utc)
        fecha_evento = evento_in.fecha_evento or timestamp_evento.date()
        event_data_dict['usuario_id'] = current_user.id
        event_data_dict['timestamp_evento'] = timestamp_evento
        event_data_dict['fecha_evento'] = fecha_evento
        db_neumatico: Optional[Neumatico] = None
        if tipo_evento == TipoEventoNeumaticoEnum.COMPRA:
            db_neumatico = await self._handle_compra(evento_in, current_user)
            event_data_dict['neumatico_id'] = db_neumatico.id
        else:
            if not evento_in.neumatico_id: raise ValidationError("neumatico_id requerido.")
            db_neumatico = await self._get_neumatico_for_update(evento_in.neumatico_id)
            event_data_dict['neumatico_id'] = db_neumatico.id
            neumatico_modificado = False
            match tipo_evento:
                case TipoEventoNeumaticoEnum.INSTALACION: neumatico_modificado = await self._handle_instalacion(evento_in, db_neumatico, fecha_evento)
                case TipoEventoNeumaticoEnum.DESMONTAJE: neumatico_modificado = await self._handle_desmontaje(evento_in, db_neumatico, fecha_evento)
                case TipoEventoNeumaticoEnum.INSPECCION: neumatico_modificado = await self._handle_inspeccion(evento_in, db_neumatico)
                case TipoEventoNeumaticoEnum.ROTACION: neumatico_modificado = await self._handle_rotacion(evento_in, db_neumatico, fecha_evento)
                case TipoEventoNeumaticoEnum.REPARACION_ENTRADA: neumatico_modificado = await self._handle_reparacion_entrada(evento_in, db_neumatico)
                case TipoEventoNeumaticoEnum.REPARACION_SALIDA: neumatico_modificado = await self._handle_reparacion_salida(evento_in, db_neumatico)
                case TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA: neumatico_modificado = await self._handle_reencauche_entrada(evento_in, db_neumatico)
                case TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA: neumatico_modificado = await self._handle_reencauche_salida(evento_in, db_neumatico)
                case TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO: neumatico_modificado = await self._handle_ajuste_inventario(evento_in, db_neumatico)
                case TipoEventoNeumaticoEnum.DESECHO: neumatico_modificado = await self._handle_desecho(evento_in, db_neumatico, fecha_evento)
                case _: raise ValidationError(f"Tipo de evento no soportado: {tipo_evento.value}")
            if neumatico_modificado:
                db_neumatico.actualizado_en = timestamp_evento
                db_neumatico.actualizado_por = current_user.id
            db_neumatico.fecha_ultimo_evento = timestamp_evento
            self.session.add(db_neumatico)
        db_evento = EventoNeumatico.model_validate(event_data_dict)
        self.session.add(db_evento)
        logger.info(f"Evento {tipo_evento.value} para neumático {db_neumatico.id} añadido a sesión.")
        await self.alert_service.check_and_create_alerts(db_neumatico, db_evento)
        return db_neumatico, db_evento

    # --- Métodos Helper ---
    def _calculate_km_recorridos(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico) -> int:
        """Calcula KM recorridos desde la última instalación/rotación."""
        odometro_evento = event_data.odometro_vehiculo_en_evento
        # Usar el campo correcto que añadimos al modelo Neumatico
        km_instalacion_neum = db_neumatico.km_instalacion

        # --- Lógica reactivada y validaciones ---
        if odometro_evento is None:
            logger.warning(f"No se proporcionó odómetro para evento en neumático {db_neumatico.id}. No se calcularán KM para este ciclo.")
            return 0
        if km_instalacion_neum is None:
            # Esto no debería pasar si el neumático está INSTALADO, pero es una buena guarda
            logger.warning(f"km_instalacion es None para neumático {db_neumatico.id} (estado: {db_neumatico.estado_actual}). No se pueden calcular KM para este ciclo.")
            return 0
        if odometro_evento < km_instalacion_neum:
            # Situación anómala (ej. cambio de odómetro del vehículo, error de digitación)
            logger.error(f"Odómetro del evento ({odometro_evento}) es menor que km_instalacion ({km_instalacion_neum}) para neumático {db_neumatico.id}. KM calculados para este ciclo serán 0.")
            return 0

        km_calculados = odometro_evento - km_instalacion_neum
        logger.info(f"KM Calculados para neumático {db_neumatico.id} en este ciclo: {odometro_evento} - {km_instalacion_neum} = {km_calculados}")
        return km_calculados
        # --- Fin lógica reactivada ---

    async def _handle_instalacion(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico, fecha_evento: date) -> bool:
            """Maneja la lógica de instalación."""
            logger.info(f"Procesando INSTALACION para neumático {db_neumatico.id}")
            estado_previo = db_neumatico.estado_actual
            # Permitir instalar solo desde EN_STOCK según la lógica original v9
            allowed_states = [EstadoNeumaticoEnum.EN_STOCK]
            if estado_previo not in allowed_states:
                raise ConflictError(f"Neumático {db_neumatico.id} no en estado válido ({allowed_states}) para instalación. Estado: {estado_previo.value if estado_previo else 'None'}")
            if event_data.odometro_vehiculo_en_evento is None:
                raise ValidationError("odometro_vehiculo_en_evento requerido para INSTALACION.")

            _, _ = await self._validate_and_get_vehiculo_posicion(event_data)
            await self._check_posicion_ocupada(cast(UUID, event_data.vehiculo_id), cast(UUID, event_data.posicion_id))

            # --- Asignaciones Corregidas ---
            db_neumatico.estado_actual = EstadoNeumaticoEnum.INSTALADO
            db_neumatico.ubicacion_actual_vehiculo_id = event_data.vehiculo_id
            db_neumatico.ubicacion_actual_posicion_id = event_data.posicion_id
            db_neumatico.ubicacion_almacen_id = None
            # Asignar a los campos correctos que ahora existen en el modelo
            db_neumatico.km_instalacion = event_data.odometro_vehiculo_en_evento
            db_neumatico.fecha_instalacion = fecha_evento

            # La lógica original v9 tenía 'db_neumatico.km_actuales = 0'.
            # Esto es incorrecto. El kilometraje acumulado NO se resetea al instalar.
            # Se mantiene el valor que tuviera 'kilometraje_acumulado'.
            # Simplemente se registra el 'km_instalacion' para saber dónde empezó este ciclo.
            if estado_previo == EstadoNeumaticoEnum.EN_STOCK:
                logger.info(f"Detectada instalación desde EN_STOCK. KM acumulados actuales: {db_neumatico.kilometraje_acumulado}. Se inicia nuevo ciclo de uso.")
            # --- Fin Correcciones ---

            # Remover el bloque de DEBUGGING si aún existe
            # Remover los bloques try/except para setattr que estaban en v9

            logger.info(f"Neumático {db_neumatico.id} actualizado a INSTALADO.")
            return True # Indicar que hubo modificación


    async def _handle_desmontaje(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico, fecha_evento: date) -> bool:
        logger.info(f"Procesando DESMONTAJE para neumático {db_neumatico.id}")
        if db_neumatico.estado_actual != EstadoNeumaticoEnum.INSTALADO:
             raise ConflictError(f"Neumático {db_neumatico.id} no está INSTALADO.")
        if not event_data.motivo_desmontaje_destino:
             raise ValidationError("motivo_desmontaje_destino requerido.")

        # --- CORRECCIÓN AQUÍ: Calcular y sumar KM al campo correcto ---
        # Ahora llamamos a la función reactivada y corregida
        km_recorridos_ciclo = self._calculate_km_recorridos(event_data, db_neumatico)
        # Sumar los KM de este ciclo al total acumulado
        db_neumatico.kilometraje_acumulado = (db_neumatico.kilometraje_acumulado or 0) + km_recorridos_ciclo
        logger.info(f"Sumando {km_recorridos_ciclo} KM por desmontaje al neumático {db_neumatico.id}. Total acumulado: {db_neumatico.kilometraje_acumulado}")
        # -------------------------------------------------------------

        nuevo_estado = event_data.motivo_desmontaje_destino
        db_neumatico.estado_actual = nuevo_estado
        db_neumatico.ubicacion_actual_vehiculo_id = None
        db_neumatico.ubicacion_actual_posicion_id = None

        # --- CORRECCIÓN AQUÍ: Limpiar campos de instalación ---
        # Estos campos ahora existen y deben limpiarse al desmontar
        db_neumatico.km_instalacion = None
        db_neumatico.fecha_instalacion = None
        # ----------------------------------------------------

        # Lógica de asignación de ubicación/desecho (sin cambios respecto a v9)
        if nuevo_estado == EstadoNeumaticoEnum.EN_STOCK:
            almacen_destino = await self._validate_and_get_almacen(event_data.destino_almacen_id, required=True)
            db_neumatico.ubicacion_almacen_id = almacen_destino.id # type: ignore
        elif nuevo_estado == EstadoNeumaticoEnum.DESECHADO:
             if not event_data.motivo_desecho_id_evento: raise ValidationError("motivo_desecho_id_evento requerido.")
             motivo = await self.session.get(MotivoDesecho, event_data.motivo_desecho_id_evento)
             if not motivo: raise ValidationError(f"Motivo desecho ID {event_data.motivo_desecho_id_evento} no encontrado.")
             db_neumatico.motivo_desecho_id = event_data.motivo_desecho_id_evento
             db_neumatico.fecha_desecho = fecha_evento
             db_neumatico.ubicacion_almacen_id = None # Asegurar que no quede en almacén
        elif nuevo_estado in [EstadoNeumaticoEnum.EN_REPARACION, EstadoNeumaticoEnum.EN_REENCAUCHE]:
            db_neumatico.ubicacion_almacen_id = None # No va a almacén si va directo a taller
            # Validar proveedor si es necesario según reglas de negocio
            await self._validate_and_get_proveedor(event_data.proveedor_servicio_id, required=False) # O True si es mandatorio
        else:
            db_neumatico.ubicacion_almacen_id = None # Por defecto, limpiar ubicación almacén

        logger.info(f"Neumático {db_neumatico.id} actualizado a {nuevo_estado.value}.")
        return True



    async def _handle_inspeccion(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico) -> bool:
        logger.info(f"Procesando INSPECCION para neumático {db_neumatico.id}")
        if db_neumatico.estado_actual != EstadoNeumaticoEnum.INSTALADO:
             raise ValidationError(f"Neumático {db_neumatico.id} debe estar INSTALADO para inspección.")

        # --- CORRECCIÓN AQUÍ ---
        # La inspección es un registro puntual. No modifica el KM acumulado.
        # Tampoco actualizaremos campos directos en Neumatico como 'profundidad_remanente_actual_mm'
        # o 'presion_actual_psi' porque no existen en el modelo.
        # La información de profundidad/presión de esta inspección se guarda en el EventoNeumatico.
        # Si se necesita mostrar la "última" medición en algún lado, se debería consultar el último evento.

        modificado = False # Indica que no se modificaron campos directos en el objeto Neumatico

        # Loguear los datos recibidos en la inspección (si existen)
        if event_data.profundidad_remanente_mm is not None:
            logger.info(f"Inspección neumático {db_neumatico.id}: Profundidad registrada {event_data.profundidad_remanente_mm} mm.")
        if event_data.presion_psi is not None:
            logger.info(f"Inspección neumático {db_neumatico.id}: Presión registrada {event_data.presion_psi} PSI.")
        # -----------------------

        logger.info(f"Neumático {db_neumatico.id} inspeccionado. ¿Modificado directamente?: {modificado}")
        # Devuelve False porque no cambiamos atributos directos del objeto db_neumatico
        # El cambio principal es la creación del registro de evento asociado.
        return modificado
    

    async def _handle_rotacion(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico, fecha_evento: date) -> bool:
        logger.info(f"Procesando ROTACION para neumático {db_neumatico.id}")
        if db_neumatico.estado_actual != EstadoNeumaticoEnum.INSTALADO:
             raise ConflictError(f"Neumático {db_neumatico.id} debe estar INSTALADO para rotar.")
        if event_data.odometro_vehiculo_en_evento is None:
             raise ValidationError("odometro_vehiculo_en_evento requerido para ROTACION.")

        _, nueva_posicion = await self._validate_and_get_vehiculo_posicion(event_data)
        # Validar que el vehículo sea el mismo (si no, sería un error de lógica o un 'traslado')
        if event_data.vehiculo_id != db_neumatico.ubicacion_actual_vehiculo_id:
             raise ValidationError(f"Rotación solo permitida dentro del mismo vehículo ({db_neumatico.ubicacion_actual_vehiculo_id}).")
        # Validar que la posición sea diferente
        if event_data.posicion_id == db_neumatico.ubicacion_actual_posicion_id:
             raise ValidationError(f"Rotación a la misma posición ({db_neumatico.ubicacion_actual_posicion_id}) no permitida.")

        # Revisar si la nueva posición está ocupada (excepto por el neumático actual si se está intercambiando)
        await self._check_posicion_ocupada(cast(UUID, event_data.vehiculo_id), cast(UUID, event_data.posicion_id), db_neumatico.id) # Permitir rotar a una posición si el ocupante es el mismo neumático? No, eso se valida arriba.

        # --- CORRECCIÓN AQUÍ: Calcular y sumar KM ---
        # Calcular y sumar KM del ciclo actual ANTES de actualizar la posición/km_instalacion
        km_recorridos_ciclo = self._calculate_km_recorridos(event_data, db_neumatico)
        db_neumatico.kilometraje_acumulado = (db_neumatico.kilometraje_acumulado or 0) + km_recorridos_ciclo
        logger.info(f"Sumando {km_recorridos_ciclo} KM por rotación al neumático {db_neumatico.id}. Total acumulado: {db_neumatico.kilometraje_acumulado}")
        # -------------------------------------------

        # Actualizar a la nueva posición y reiniciar datos de instalación para el nuevo ciclo
        db_neumatico.ubicacion_actual_posicion_id = event_data.posicion_id
        db_neumatico.ubicacion_almacen_id = None # Sigue instalado

        # --- CORRECCIÓN AQUÍ: Asignar directamente km/fecha instalación ---
        db_neumatico.km_instalacion = event_data.odometro_vehiculo_en_evento # Nuevo inicio de ciclo
        db_neumatico.fecha_instalacion = fecha_evento # Fecha de inicio del nuevo ciclo
        # -----------------------------------------------------------------

        logger.info(f"Neumático {db_neumatico.id} rotado a posición {db_neumatico.ubicacion_actual_posicion_id}.")
        return True




    async def _handle_reparacion_entrada(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico) -> bool:
        # ... (sin cambios) ...
        logger.info(f"Procesando REPARACION_ENTRADA para neumático {db_neumatico.id}")
        if db_neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO: raise ConflictError("Desmontar antes de reparar.")
        await self._validate_and_get_proveedor(event_data.proveedor_servicio_id, required=False)
        db_neumatico.estado_actual = EstadoNeumaticoEnum.EN_REPARACION
        db_neumatico.ubicacion_actual_vehiculo_id = None; db_neumatico.ubicacion_actual_posicion_id = None; db_neumatico.ubicacion_almacen_id = None
        logger.info(f"Neumático {db_neumatico.id} actualizado a EN_REPARACION.")
        return True

    async def _handle_reparacion_salida(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico) -> bool:
        # ... (sin cambios) ...
        logger.info(f"Procesando REPARACION_SALIDA para neumático {db_neumatico.id}")
        if db_neumatico.estado_actual != EstadoNeumaticoEnum.EN_REPARACION: raise ConflictError(f"Neumático {db_neumatico.id} no está EN_REPARACION.")
        almacen_destino = await self._validate_and_get_almacen(event_data.destino_almacen_id)
        await self._validate_and_get_proveedor(event_data.proveedor_servicio_id, required=False)
        db_neumatico.estado_actual = EstadoNeumaticoEnum.EN_STOCK
        db_neumatico.ubicacion_almacen_id = almacen_destino.id # type: ignore
        db_neumatico.ubicacion_actual_vehiculo_id = None; db_neumatico.ubicacion_actual_posicion_id = None
        logger.info(f"Neumático {db_neumatico.id} actualizado a EN_STOCK post-reparación.")
        return True

    async def _handle_reencauche_entrada(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico) -> bool:
        logger.info(f"Procesando REENCAUCHE_ENTRADA para neumático {db_neumatico.id}")
        if db_neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO: raise ConflictError("Desmontar antes de reencauchar.")
        await self._validate_and_get_proveedor(event_data.proveedor_servicio_id)

        # --- CORRECCIÓN v8: Validación límite (usando nombre correcto y carga explícita) ---
        modelo_neum = None
        if db_neumatico.modelo_id:
            modelo_neum = await self.session.get(ModeloNeumatico, db_neumatico.modelo_id)

        if modelo_neum and modelo_neum.reencauches_maximos is not None:
             reencauches_previos = db_neumatico.reencauches_realizados or 0 # <-- Usar nombre correcto
             if reencauches_previos >= modelo_neum.reencauches_maximos:
                 raise ValidationError(f"Neumático {db_neumatico.id} alcanzó límite de {modelo_neum.reencauches_maximos} reencauches.")
        elif not modelo_neum and db_neumatico.modelo_id:
             logger.warning(f"Modelo ID {db_neumatico.modelo_id} no encontrado para validar límite.")
        # --- FIN CORRECCIÓN v8 ---

        db_neumatico.estado_actual = EstadoNeumaticoEnum.EN_REENCAUCHE
        db_neumatico.ubicacion_actual_vehiculo_id = None; db_neumatico.ubicacion_actual_posicion_id = None; db_neumatico.ubicacion_almacen_id = None
        logger.info(f"Neumático {db_neumatico.id} actualizado a EN_REENCAUCHE.")
        return True


    async def _handle_reencauche_salida(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico) -> bool:
        logger.info(f"Procesando REENCAUCHE_SALIDA para neumático {db_neumatico.id}")
        if db_neumatico.estado_actual != EstadoNeumaticoEnum.EN_REENCAUCHE: raise ConflictError(f"Neumático {db_neumatico.id} no está EN_REENCAUCHE.")
        if event_data.profundidad_post_reencauche_mm is None: raise ValidationError("profundidad_post_reencauche_mm requerida.")
        almacen_destino = await self._validate_and_get_almacen(event_data.destino_almacen_id, required=True) # Asegurar que es requerido
        await self._validate_and_get_proveedor(event_data.proveedor_servicio_id, required=False) # Proveedor es opcional aquí?

        # Validación de límite (ya presente en v9 y parece correcta)
        modelo_neum = None
        if db_neumatico.modelo_id:
            modelo_neum = await self.session.get(ModeloNeumatico, db_neumatico.modelo_id)

        # Añadir manejo si el modelo no se encuentra
        if not modelo_neum:
             logger.error(f"No se pudo cargar ModeloNeumatico con ID {db_neumatico.modelo_id} para neumático {db_neumatico.id}")
             raise ServiceError("No se pudo obtener la información del modelo del neumático.")

        # Verificar si permite reencauche (importante)
        if not modelo_neum.permite_reencauche:
             raise ConflictError(f"Modelo {modelo_neum.nombre_modelo} no permite reencauche.")

        if modelo_neum.reencauches_maximos is not None:
             reencauches_previos = db_neumatico.reencauches_realizados or 0
             # Esta validación aquí es una segunda capa, la principal está en _handle_reencauche_entrada
             if reencauches_previos >= modelo_neum.reencauches_maximos:
                 logger.error(f"REENCAUCHE_SALIDA: Neumático {db_neumatico.id} ya alcanzó límite (Error lógico si entró a reencauche).")
                 raise ConflictError(f"Neumático {db_neumatico.id} alcanzó límite de reencauches.")


        if db_neumatico.reencauches_realizados is None:
            db_neumatico.reencauches_realizados = 0

        db_neumatico.estado_actual = EstadoNeumaticoEnum.EN_STOCK
        db_neumatico.ubicacion_almacen_id = almacen_destino.id # type: ignore
        db_neumatico.ubicacion_actual_vehiculo_id = None; db_neumatico.ubicacion_actual_posicion_id = None
        db_neumatico.reencauches_realizados += 1
        # --- CORRECCIÓN AQUÍ ---
        db_neumatico.kilometraje_acumulado = 0 # Resetear KM acumulados
        # -----------------------
        db_neumatico.es_reencauchado = True
        db_neumatico.profundidad_inicial_mm = event_data.profundidad_post_reencauche_mm # Actualizar profundidad inicial
        # Limpiar datos de instalación si los hubiera
        db_neumatico.km_instalacion = None
        db_neumatico.fecha_instalacion = None

        logger.info(f"Neumático {db_neumatico.id} actualizado post-reencauche. Reencauche #{db_neumatico.reencauches_realizados}. KM reseteados.")
        return True


    async def _handle_ajuste_inventario(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico) -> bool:
        # ... (Sin cambios) ...
        logger.info(f"Procesando AJUSTE_INVENTARIO para neumático {db_neumatico.id}")
        estado_ajuste_enum = event_data.estado_ajuste
        if estado_ajuste_enum is None: raise ValidationError("estado_ajuste requerido.")
        if not isinstance(estado_ajuste_enum, EstadoNeumaticoEnum): raise ValidationError(f"Valor inválido para estado_ajuste: {estado_ajuste_enum}")
        almacen_destino = await self._validate_and_get_almacen(event_data.destino_almacen_id)
        db_neumatico.estado_actual = estado_ajuste_enum
        db_neumatico.ubicacion_almacen_id = almacen_destino.id # type: ignore
        db_neumatico.ubicacion_actual_vehiculo_id = None; db_neumatico.ubicacion_actual_posicion_id = None
        logger.info(f"Neumático {db_neumatico.id} ajustado a {estado_ajuste_enum.value} en {almacen_destino.id}.") # type: ignore
        return True

    async def _handle_desecho(self, event_data: EventoNeumaticoCreate, db_neumatico: Neumatico, fecha_evento: date) -> bool:
        logger.info(f"Procesando DESECHO para neumático {db_neumatico.id}")
        # Estados desde los que se permite desechar (cualquiera menos INSTALADO)
        forbidden_states = [EstadoNeumaticoEnum.INSTALADO]
        if db_neumatico.estado_actual in forbidden_states:
            raise ConflictError(f"No se puede desechar neumático {db_neumatico.id} mientras está {db_neumatico.estado_actual.value}. Desmontar primero.")

        if not event_data.motivo_desecho_id_evento:
             raise ValidationError("motivo_desecho_id_evento requerido para DESECHO.")
        motivo = await self.session.get(MotivoDesecho, event_data.motivo_desecho_id_evento)
        if not motivo: raise ValidationError(f"Motivo desecho ID {event_data.motivo_desecho_id_evento} no encontrado.")

        db_neumatico.estado_actual = EstadoNeumaticoEnum.DESECHADO
        db_neumatico.motivo_desecho_id = event_data.motivo_desecho_id_evento
        db_neumatico.fecha_desecho = fecha_evento
        # Limpiar todas las ubicaciones y datos de ciclo de uso
        db_neumatico.ubicacion_actual_vehiculo_id = None
        db_neumatico.ubicacion_actual_posicion_id = None
        db_neumatico.ubicacion_almacen_id = None
        # --- CORRECCIÓN AQUÍ: Limpieza directa de campos ---
        db_neumatico.km_instalacion = None
        db_neumatico.fecha_instalacion = None
        # ----------------------------------------------------

        logger.info(f"Neumático {db_neumatico.id} actualizado a DESECHADO.")
        return True