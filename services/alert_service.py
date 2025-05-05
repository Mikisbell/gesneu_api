# services/alert_service.py (Corregido y Reestructurado)
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
# Asegúrate que estas Enums existen en models.common o ajústalo
from models.neumatico import EstadoNeumaticoEnum             # <-- LÍNEA CORRECTA 1
from models.parametro_inventario import TipoParametroEnum   # <-- LÍNEA CORRECTA 2
# Importar TipoEventoNeumaticoEnum desde su ubicación correcta
from models.evento_neumatico import TipoEventoNeumaticoEnum


logger = logging.getLogger(__name__)

# --- Función HELPER para convertir Decimal en el contexto ---
# (Movida dentro de la clase o dejada fuera si se usa en otros sitios también)
def _convert_context_for_json(context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convierte valores Decimal a float dentro de un diccionario para serialización JSON."""
    if context is None:
        return None
    new_context = {}
    for k, v in context.items():
        if isinstance(v, Decimal):
            new_context[k] = float(v) # Convertir Decimal a float
        elif isinstance(v, uuid.UUID):
             new_context[k] = str(v) # Convertir UUID a string
        # Añadir otras conversiones si son necesarias
        else:
            new_context[k] = v
    return new_context
# ----------------------------------------------------------

class AlertService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _crear_alerta_en_db(
        self,
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
        (Ahora es un método de la clase)
        """
        try:
            datos_contexto_serializable = _convert_context_for_json(datos_contexto)

            stmt_existente = select(Alerta).where(
                Alerta.tipo_alerta == tipo_alerta,
                Alerta.estado_alerta != 'GESTIONADA', # Usar estado_alerta
                Alerta.neumatico_id == neumatico_id,
                Alerta.modelo_id == modelo_id,
                Alerta.almacen_id == almacen_id,
                Alerta.vehiculo_id == vehiculo_id
                # Podríamos querer refinar esta lógica de duplicados
            )
            result_existente = await self.session.exec(stmt_existente)
            alerta_existente = result_existente.first()

            if alerta_existente:
                logger.info(f"Alerta '{tipo_alerta}' similar (ID: {alerta_existente.id}) ya existe y no está gestionada. No se crea una nueva.")
                return alerta_existente # Devolver la existente

            nueva_alerta = Alerta(
                tipo_alerta=tipo_alerta,
                mensaje=mensaje,
                nivel_severidad=nivel_severidad,
                estado_alerta='NUEVA', # Estado inicial
                neumatico_id=neumatico_id,
                modelo_id=modelo_id,
                almacen_id=almacen_id,
                vehiculo_id=vehiculo_id,
                parametro_id=parametro_id,
                datos_contexto=datos_contexto_serializable # Usar el contexto serializado
            )
            self.session.add(nueva_alerta)
            # El commit debe hacerse fuera, idealmente al final de la transacción del evento
            # await self.session.commit() # Quitar commit de aquí
            await self.session.flush() # Para asegurar que la alerta se inserte antes de refresh
            await self.session.refresh(nueva_alerta)
            logger.info(f"Alerta '{tipo_alerta}' creada con ID: {nueva_alerta.id}")
            return nueva_alerta
        except Exception as e:
            # No hacer rollback aquí, dejar que la transacción principal falle si es necesario
            # await self.session.rollback()
            logger.error(f"Error al preparar/verificar alerta '{tipo_alerta}' en DB: {e}", exc_info=True)
            # Propagar el error podría ser mejor que devolver None
            # return None
            raise e # Propagar error para que la transacción falle

    async def _check_profundidad_baja(self, neumatico: Neumatico, evento: EventoNeumatico):
        """Verifica si la profundidad en un evento de inspección está bajo el umbral."""
        # Solo aplica a eventos de inspección con profundidad medida
        if evento.tipo_evento != TipoEventoNeumaticoEnum.INSPECCION or evento.profundidad_remanente_mm is None:
            return

        try:
            # El neumático ya se pasa como argumento
            if not neumatico or not neumatico.modelo_id:
                logger.warning(f"Datos incompletos de neumático {evento.neumatico_id} en _check_profundidad_baja.")
                return

            modelo_id = neumatico.modelo_id

            # Buscar parámetro de profundidad mínima
            stmt_umbral = select(ParametroInventario).where(
                ParametroInventario.tipo_parametro == TipoParametroEnum.PROFUNDIDAD_MINIMA,
                ParametroInventario.modelo_id == modelo_id,
                ParametroInventario.activo == True,
                # Priorizar parámetro específico de almacén si existe, sino el general
                (ParametroInventario.almacen_id == neumatico.ubicacion_almacen_id) | (ParametroInventario.almacen_id.is_(None))
            ).order_by(
                ParametroInventario.almacen_id.desc().nulls_last() # El específico (not None) primero
            )
            resultado_umbral = await self.session.exec(stmt_umbral)
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
                    "modelo_id": modelo_id,
                    "neumatico_id": neumatico.id,
                    "evento_id": evento.id # ID del evento que disparó la alerta
                }
                await self._crear_alerta_en_db(
                    tipo_alerta='PROFUNDIDAD_BAJA',
                    mensaje=mensaje,
                    nivel_severidad='WARN', # O 'ERROR' según criticidad
                    neumatico_id=neumatico.id,
                    modelo_id=modelo_id,
                    parametro_id=parametro.id,
                    datos_contexto=contexto
                )
            else:
                 # Si la profundidad es OK, resolver alertas abiertas de profundidad baja para este neumático
                 stmt_resolver = select(Alerta).where(
                     Alerta.tipo_alerta == 'PROFUNDIDAD_BAJA',
                     Alerta.neumatico_id == neumatico.id,
                     Alerta.estado_alerta != 'GESTIONADA' # Solo resolver las no gestionadas
                 )
                 res_resolver = await self.session.exec(stmt_resolver)
                 alertas_a_resolver = res_resolver.all()
                 for alerta in alertas_a_resolver:
                     alerta.estado_alerta = 'GESTIONADA'
                     alerta.timestamp_gestion = datetime.now(timezone.utc)
                     alerta.notas_resolucion = f"Resuelta automáticamente por inspección con profundidad {profundidad_medida:.1f}mm >= umbral {umbral_minimo:.1f}mm."
                     self.session.add(alerta) # Añadir a la sesión para guardar cambios
                 if alertas_a_resolver:
                     # await self.session.commit() # No hacer commit aquí
                     await self.session.flush() # Asegurar que los cambios se envíen a la BD
                     logger.info(f"Resueltas {len(alertas_a_resolver)} alertas de profundidad baja para neumático {neumatico.id}")

        except Exception as e:
            logger.error(f"Error no crítico en _check_profundidad_baja para evento {evento.id}: {e}", exc_info=True)


    async def _check_stock_minimo(self, modelo_id: uuid.UUID, almacen_id: uuid.UUID):
        """Verifica si el stock de un modelo en un almacén está bajo el mínimo."""
        # Esta función podría llamarse después de eventos que cambian el stock (COMPRA, DESMONTAJE a stock, etc.)
        try:
            # Contar stock actual
            stmt_stock = select(func.count(Neumatico.id)).where(
                Neumatico.estado_actual == EstadoNeumaticoEnum.EN_STOCK,
                Neumatico.modelo_id == modelo_id,
                Neumatico.ubicacion_almacen_id == almacen_id
            )
            result_stock = await self.session.exec(stmt_stock)
            # --- Corrección: Usar scalar() en lugar de scalar_one() o first() para count ---
            stock_actual = result_stock.scalar() or 0
            # --- Fin Corrección ---


            # Buscar parámetro de stock mínimo
            stmt_param = select(ParametroInventario).where(
                ParametroInventario.tipo_parametro == TipoParametroEnum.NIVEL_MINIMO,
                ParametroInventario.modelo_id == modelo_id,
                ParametroInventario.activo == True,
                (ParametroInventario.almacen_id == almacen_id) | (ParametroInventario.almacen_id.is_(None))
            ).order_by(
                ParametroInventario.almacen_id.desc().nulls_last()
            )
            resultado_param = await self.session.exec(stmt_param)
            parametro = resultado_param.first()

            if not parametro or parametro.valor_numerico is None:
                logger.debug(f"No se encontró nivel mínimo de stock activo para modelo {modelo_id} en almacén {almacen_id}.")
                return

            nivel_minimo = parametro.valor_numerico

            if stock_actual < nivel_minimo:
                # Solo crear alerta si no existe ya una abierta para este modelo/almacén
                modelo = await self.session.get(ModeloNeumatico, modelo_id)
                almacen = await self.session.get(Almacen, almacen_id)
                nombre_modelo = modelo.nombre_modelo if modelo else str(modelo_id)
                nombre_almacen = almacen.nombre if almacen else str(almacen_id)

                mensaje = (
                    f"Stock bajo mínimo para {nombre_modelo} en {nombre_almacen} "
                    f"({stock_actual} < {nivel_minimo:.0f})."
                )
                contexto = {
                    "stock_actual": stock_actual,
                    "nivel_minimo": nivel_minimo,
                    "modelo_id": modelo_id,
                    "almacen_id": almacen_id
                }
                await self._crear_alerta_en_db(
                    tipo_alerta='STOCK_MINIMO',
                    mensaje=mensaje,
                    nivel_severidad='WARN',
                    modelo_id=modelo_id,
                    almacen_id=almacen_id,
                    parametro_id=parametro.id,
                    datos_contexto=contexto
                )
            else:
                 # Si el stock es OK, resolver alertas abiertas de stock mínimo para este modelo/almacén
                 stmt_resolver = select(Alerta).where(
                     Alerta.tipo_alerta == 'STOCK_MINIMO',
                     Alerta.modelo_id == modelo_id,
                     Alerta.almacen_id == almacen_id,
                     Alerta.estado_alerta != 'GESTIONADA'
                 )
                 res_resolver = await self.session.exec(stmt_resolver)
                 alertas_a_resolver = res_resolver.all()
                 for alerta in alertas_a_resolver:
                     alerta.estado_alerta = 'GESTIONADA'
                     alerta.timestamp_gestion = datetime.now(timezone.utc)
                     alerta.notas_resolucion = f"Resuelta automáticamente. Stock actual {stock_actual} >= mínimo {nivel_minimo:.0f}."
                     self.session.add(alerta)
                 if alertas_a_resolver:
                     # await self.session.commit() # No hacer commit aquí
                     await self.session.flush()
                     logger.info(f"Resueltas {len(alertas_a_resolver)} alertas de stock mínimo para modelo {modelo_id} en almacén {almacen_id}")

        except Exception as e:
             logger.error(f"Error no crítico en _check_stock_minimo para modelo {modelo_id}, almacén {almacen_id}: {e}", exc_info=True)


    # --- *** Nuevo Método Público *** ---
    async def check_and_create_alerts(self, neumatico: Neumatico, evento: EventoNeumatico):
        """
        Método principal para verificar todas las condiciones de alerta
        relevantes para un neumático después de un evento.
        """
        logger.debug(f"Iniciando check_and_create_alerts para neumático {neumatico.id} tras evento {evento.tipo_evento}")

        # 1. Verificar profundidad baja (si aplica al evento)
        await self._check_profundidad_baja(neumatico, evento)

        # 2. Verificar stock mínimo (si el evento afecta el stock)
        #    Eventos que ponen neumático EN_STOCK: COMPRA, DESMONTAJE(a stock), REPARACION_SALIDA, REENCAUCHE_SALIDA, AJUSTE(a stock)
        eventos_a_stock = [
            TipoEventoNeumaticoEnum.COMPRA,
            TipoEventoNeumaticoEnum.DESMONTAJE, # Necesita check adicional si fue a stock
            TipoEventoNeumaticoEnum.REPARACION_SALIDA,
            TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
            TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO # Necesita check adicional si fue a stock
        ]
        if evento.tipo_evento in eventos_a_stock and neumatico.estado_actual == EstadoNeumaticoEnum.EN_STOCK:
             # Asegurar que tenemos modelo_id y almacen_id
             if neumatico.modelo_id and neumatico.ubicacion_almacen_id:
                 logger.debug(f"Evento {evento.tipo_evento} resultó en EN_STOCK. Verificando stock mínimo para M:{neumatico.modelo_id} A:{neumatico.ubicacion_almacen_id}")
                 await self._check_stock_minimo(neumatico.modelo_id, neumatico.ubicacion_almacen_id)
             else:
                 logger.warning(f"Faltan modelo_id o ubicacion_almacen_id para verificar stock mínimo tras evento {evento.tipo_evento} en neumático {neumatico.id}")

        # 3. Añadir aquí llamadas a otras funciones de verificación de alertas
        #    Ejemplo: await self._check_presion_anormal(neumatico, evento)
        #    Ejemplo: await self._check_tiempo_uso_excedido(neumatico)
        #    Ejemplo: await self._check_km_excedidos(neumatico)

        logger.debug(f"Finalizado check_and_create_alerts para neumático {neumatico.id}")
    # --- *** Fin Nuevo Método Público *** ---


# --- Fin del archivo ---