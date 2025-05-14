# services/alert_service.py (Corregido y Reestructurado)
import uuid
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
import json
from utils.uuid_utils import safe_uuid, safe_str_uuid, safe_dict_uuid_to_str
from utils.safe_uuid import SafeUUID, patch_uuid_class

# Apply UUID patch to handle string methods
patch_uuid_class()
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


from schemas.common import TipoAlertaEnum # Importar TipoAlertaEnum

logger = logging.getLogger(__name__)

# --- Función HELPER para convertir Decimal en el contexto ---
# (Movida dentro de la clase o dejada fuera si se usa en otros sitios también)
def _convert_context_for_json(context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convierte valores complejos a tipos serializables por JSON."""
    if context is None:
        return None
    
    def convert_value(v):
        """Convierte un valor individual al tipo adecuado para JSON."""
        try:
            if isinstance(v, Decimal):
                return float(v)  # Convertir Decimal a float
            elif isinstance(v, uuid.UUID):
                return str(v)  # Convertir UUID a string
            elif hasattr(v, 'id') and isinstance(v.id, uuid.UUID):
                # Si es un objeto con una propiedad ID que es UUID, convertirla
                return str(v.id)  # Obtener el UUID como string
            elif isinstance(v, datetime):
                return v.isoformat()  # Convertir datetime a ISO string
            elif isinstance(v, date):
                return v.isoformat()  # Convertir date a ISO string
            elif isinstance(v, dict):
                return {k: convert_value(val) for k, val in v.items()}  # Procesar diccionarios anidados
            elif isinstance(v, (list, tuple)):
                return [convert_value(item) for item in v]  # Procesar listas y tuplas
            else:
                # Intentar convertir a string como último recurso si el objeto no es serializable
                try:
                    json.dumps({"test": v})
                    return v  # Si es serializable, dejarlo como está
                except (TypeError, OverflowError):
                    return str(v)  # Si no es serializable, convertir a string
        except Exception as e:
            # Último recurso: si hay alguna excepción en la conversión, devolver string
            logger.warning(f"Error al convertir valor para JSON: {e}. Se convierte a string.")
            try:
                return str(v)
            except:
                return "[Valor no convertible]"
    
    # Procesar el diccionario completo
    result = {}
    for k, v in context.items():
        try:
            result[k] = convert_value(v)
        except Exception as e:
            logger.warning(f"Error al procesar clave {k}: {e}. Se omite esta clave.")
            result[k] = str(v)
    
    return result
# ----------------------------------------------------------

class AlertService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _generar_descripcion_alerta(self, tipo_alerta: str, context_data: Optional[Dict[str, Any]]) -> str:
        """Genera una descripción detallada para la alerta basada en su tipo y contexto."""
        if context_data is None:
            context_data = {}
        
        # Convertir UUID a strings para evitar errores
        safe_context = {}
        for k, v in context_data.items():
            if isinstance(v, uuid.UUID):
                safe_context[k] = str(v)
            else:
                safe_context[k] = v
            
        # Si hay una descripción personalizada en el contexto, usarla
        if 'descripcion_personalizada' in safe_context:
            return safe_context['descripcion_personalizada']

        if tipo_alerta == TipoAlertaEnum.PROFUNDIDAD_BAJA.value:
            profundidad = safe_context.get('profundidad_medida_mm')
            umbral = safe_context.get('umbral_minimo_mm')
            if profundidad is not None and umbral is not None:
                 return f"Profundidad medida ({profundidad:.1f}mm) <= umbral mínimo ({umbral:.1f}mm)."
            return "Alerta de profundidad baja detectada."
            
        elif tipo_alerta == TipoAlertaEnum.LIMITE_REENCAUCHES_ALCANZADO.value:
            reencauches_realizados = safe_context.get('reencauches_realizados')
            reencauches_maximos = safe_context.get('reencauches_maximos')
            numero_serie = safe_context.get('numero_serie', 'N/A')
            modelo_nombre = safe_context.get('modelo_nombre', 'N/A')
            medida = safe_context.get('medida', 'N/A')
            
            if reencauches_realizados is not None and reencauches_maximos is not None:
                return f"El neumático {numero_serie} ha alcanzado el límite de {reencauches_maximos} reencauches. Modelo: {modelo_nombre} {medida}. Este neumático no debe ser reencauchado nuevamente."
            return "Neumático ha alcanzado el límite de reencauches permitidos."

        elif tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value:
            motivos = safe_context.get('motivos', [])
            razones = safe_context.get('razones', [])
            if motivos and razones:
                return f"Fin de vida útil estimada: {', '.join(motivos)}. {' '.join(razones)}"
            return "Neumático ha alcanzado su fin de vida útil estimada."

        # Añadir lógica para otros tipos de alerta si es necesario
        # elif tipo_alerta == TipoAlertaEnum.STOCK_MINIMO.value:
        #     stock = safe_context.get('stock_actual')
        #     minimo = safe_context.get('nivel_minimo')
        #     modelo_id = safe_context.get('modelo_id')
        #     almacen_id = safe_context.get('almacen_id')
        #     return f"Stock bajo ({stock}) para modelo {modelo_id} en almacén {almacen_id} (mínimo {minimo})."

        return f"Alerta tipo {tipo_alerta} detectada." # Descripción por defecto

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
            # Usar nuestras funciones safe para manejar UUIDs de forma segura
            neumatico_uuid = safe_uuid(neumatico_id)
            modelo_uuid = safe_uuid(modelo_id)
            almacen_uuid = safe_uuid(almacen_id)
            vehiculo_uuid = safe_uuid(vehiculo_id)
            parametro_uuid = safe_uuid(parametro_id)
            
            # También guardar versiones string para logging y uso en datos_contexto
            neumatico_id_str = safe_str_uuid(neumatico_id)
            modelo_id_str = safe_str_uuid(modelo_id)
            almacen_id_str = safe_str_uuid(almacen_id)
            vehiculo_id_str = safe_str_uuid(vehiculo_id)
            parametro_id_str = safe_str_uuid(parametro_id)
            
            # Asegurarse de que todos los UUIDs en datos_contexto estén convertidos a string
            if datos_contexto:
                datos_contexto = safe_dict_uuid_to_str(datos_contexto)
            
            # Convertir cualquier otro tipo complejo a formato serializable JSON
            datos_contexto_serializable = _convert_context_for_json(datos_contexto)

            # Construir consulta para verificar alertas existentes
            stmt_existente = select(Alerta).where(
                Alerta.tipo_alerta == tipo_alerta,
                Alerta.resuelta == False
            )
            
            # Añadir condiciones de forma condicional solo si no son None
            if neumatico_uuid:
                stmt_existente = stmt_existente.where(Alerta.neumatico_id == neumatico_uuid)
            if modelo_uuid:
                stmt_existente = stmt_existente.where(Alerta.modelo_id == modelo_uuid)
            if almacen_uuid:
                stmt_existente = stmt_existente.where(Alerta.almacen_id == almacen_uuid)
            if vehiculo_uuid:
                stmt_existente = stmt_existente.where(Alerta.vehiculo_id == vehiculo_uuid)
            
            result_existente = await self.session.exec(stmt_existente)
            alerta_existente = result_existente.first()

            if alerta_existente:
                logger.info(f"Alerta '{tipo_alerta}' similar (ID: {alerta_existente.id}) ya existe y no está gestionada. No se crea una nueva.")
                return alerta_existente # Devolver la existente

            # Generar la descripción usando el método helper
            descripcion_generada = self._generar_descripcion_alerta(tipo_alerta, datos_contexto_serializable)

            # Crear la alerta asegurando que los UUIDs sean objetos UUID válidos
            nueva_alerta = Alerta(
                tipo_alerta=tipo_alerta,
                descripcion=descripcion_generada,
                nivel_severidad=nivel_severidad,
                resuelta=False, # Estado inicial: no resuelta
                neumatico_id=neumatico_uuid,
                modelo_id=modelo_uuid,
                almacen_id=almacen_uuid,
                vehiculo_id=vehiculo_uuid,
                parametro_id=parametro_uuid,
                datos_contexto=datos_contexto_serializable
            )
            self.session.add(nueva_alerta)
            await self.session.flush() # Para asegurar que la alerta se inserte antes de refresh
            await self.session.refresh(nueva_alerta)
            logger.info(f"Alerta '{tipo_alerta}' creada con ID: {nueva_alerta.id}")
            return nueva_alerta
        except Exception as e:
            logger.error(f"Error al preparar/verificar alerta '{tipo_alerta}' en DB: {e}", exc_info=True)
            raise e # Propagar error para que la transacción falle

    async def _check_profundidad_baja(self, neumatico: Neumatico, evento):
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
                    "evento_id": getattr(evento, 'id', None)
                }
                await self._crear_alerta_en_db(
                    tipo_alerta='PROFUNDIDAD_BAJA',
                    # Asegurar que el mensaje es un string, incluso si la construcción falla
                    mensaje=str(mensaje) if mensaje is not None else "Alerta de profundidad baja (mensaje no disponible)",
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
                     # Corregido: Usar el campo booleano 'resuelta'
                     Alerta.resuelta == False # Solo resolver las no resueltas
                 )
                 res_resolver = await self.session.exec(stmt_resolver)
                 alertas_a_resolver = res_resolver.all()
                 for alerta in alertas_a_resolver:
                     # Corregido: Marcar como resuelta
                     alerta.resuelta = True
                     alerta.timestamp_gestion = datetime.now(timezone.utc)
                     alerta.notas_resolucion = f"Resuelta automáticamente por inspección con profundidad {profundidad_medida:.1f}mm >= umbral {umbral_minimo:.1f}mm."
                     self.session.add(alerta) # Añadir a la sesión para guardar cambios
                 if alertas_a_resolver:
                     # await self.session.commit() # No hacer commit aquí
                     await self.session.flush() # Asegurar que los cambios se envíen a la BD
                     logger.info(f"Resueltas {len(alertas_a_resolver)} alertas de profundidad baja para neumático {neumatico.id}")

        except Exception as e:
            evento_id = getattr(evento, 'id', 'no_id')
            logger.error(f"Error no crítico en _check_profundidad_baja para evento {evento_id}: {e}", exc_info=True)


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
                     # Corregido: Usar el campo booleano 'resuelta'
                     Alerta.resuelta == False
                 )
                 res_resolver = await self.session.exec(stmt_resolver)
                 alertas_a_resolver = res_resolver.all()
                 for alerta in alertas_a_resolver:
                     # Corregido: Marcar como resuelta
                     alerta.resuelta = True
                     alerta.timestamp_gestion = datetime.now(timezone.utc)
                     alerta.notas_resolucion = f"Resuelta automáticamente. Stock actual {stock_actual} >= mínimo {nivel_minimo:.0f}."
                     self.session.add(alerta)
                 if alertas_a_resolver:
                     # await self.session.commit() # No hacer commit aquí
                     await self.session.flush()
                     logger.info(f"Resueltas {len(alertas_a_resolver)} alertas de stock mínimo para modelo {modelo_id} en almacén {almacen_id}")

        except Exception as e:
             logger.error(f"Error no crítico en _check_stock_minimo para modelo {modelo_id}, almacén {almacen_id}: {e}", exc_info=True)


    async def _check_limite_reencauches(self, neumatico: Neumatico):
        """Verificar si un neumático ha alcanzado su límite de reencauches."""
        try:
            # Usar safe_str_uuid para manejar el ID del neumático de forma segura
            neumatico_id_str = safe_str_uuid(neumatico.id)
            
            if neumatico.modelo_id is None:
                logger.warning(f"Neumático {neumatico_id_str} sin modelo asignado, no se puede verificar límite de reencauches")
                return
                
            # Usar safe_uuid para asegurar que modelo_id sea un UUID válido
            modelo_id = safe_uuid(neumatico.modelo_id)
            if not modelo_id:
                logger.warning(f"modelo_id inválido para neumático {neumatico_id_str}")
                return
            
            # Obtener el modelo para conocer el límite de reencauches
            modelo = await self.session.get(ModeloNeumatico, modelo_id)
            if not modelo:
                logger.warning(f"Modelo {safe_str_uuid(modelo_id)} no encontrado para verificar límite de reencauches")
                return
                
            # Si el modelo no permite reencauche, no hay límite que verificar
            if not modelo.permite_reencauche:
                modelo_id_str = safe_str_uuid(modelo.id)
                logger.debug(f"El modelo {modelo_id_str} no permite reencauche, no se genera alerta de límite")
                return
            
            # Verificar si se alcanzó el límite
            if (modelo.reencauches_maximos is not None and 
                neumatico.reencauches_realizados is not None and 
                neumatico.reencauches_realizados >= modelo.reencauches_maximos):
                
                # Preparar contexto para la alerta asegurando que todos los valores sean serializables
                datos_contexto = {
                    "reencauches_realizados": neumatico.reencauches_realizados,
                    "reencauches_maximos": modelo.reencauches_maximos,
                    "modelo_nombre": modelo.nombre_modelo if modelo.nombre_modelo else "Desconocido",
                    "medida": modelo.medida if modelo.medida else "Desconocida",
                    "numero_serie": neumatico.numero_serie if neumatico.numero_serie else "Desconocido",
                    "neumatico_id": neumatico_id_str,
                    "modelo_id": safe_str_uuid(modelo.id),
                    "descripcion_personalizada": f"El neumático {neumatico.numero_serie or 'desconocido'} ha alcanzado el límite de {modelo.reencauches_maximos} reencauches. Modelo: {modelo.nombre_modelo or 'desconocido'} {modelo.medida or ''}. Este neumático no debe ser reencauchado nuevamente."
                }
                
                mensaje = f"Neumático ha alcanzado el límite de {modelo.reencauches_maximos} reencauches permitidos."
                
                # Usar los objetos UUID originales o sus versiones safe para la creación de la alerta
                await self._crear_alerta_en_db(
                    tipo_alerta=TipoAlertaEnum.LIMITE_REENCAUCHES_ALCANZADO.value,
                    mensaje=mensaje,
                    nivel_severidad="WARN",
                    neumatico_id=safe_uuid(neumatico.id),
                    modelo_id=safe_uuid(modelo.id),
                    datos_contexto=datos_contexto
                )
        except Exception as e:
            logger.error(f"Error al verificar límite de reencauches: {e}", exc_info=True)

    # --- *** Nuevo Método Público *** ---
    async def check_and_create_alerts(self, neumatico: Neumatico, evento: EventoNeumatico):
        """
        Método principal para verificar todas las condiciones de alerta
        relevantes para un neumático después de un evento.
        """
        # Crear una copia segura del neumático con UUIDs convertidos a strings para evitar problemas de UUID.replace
        try:
            # Asegurarse de que todos los IDs (UUIDs) sean strings para prevenir posibles errores
            neumatico_id_safe = str(neumatico.id) if neumatico.id else None
            logger.debug(f"Iniciando check_and_create_alerts para neumático {neumatico_id_safe} tras evento {evento.tipo_evento}")
            
            # 1. Verificar profundidad baja (si aplica al evento)
            await self._check_profundidad_baja(neumatico, evento)

            # 2. Verificar límite de reencauches alcanzado
            # Es especialmente importante verificar después de un evento de reencauche_salida
            await self._check_limite_reencauches(neumatico)

            # 3. Verificar stock mínimo (si el evento afecta el stock)
            #    Eventos que ponen neumático EN_STOCK: COMPRA, DESMONTAJE(a stock), REPARACION_SALIDA, REENCAUCHE_SALIDA, AJUSTE(a stock)
            eventos_a_stock = [
                TipoEventoNeumaticoEnum.COMPRA,
                TipoEventoNeumaticoEnum.DESMONTAJE, # Necesita check adicional si fue a stock
                TipoEventoNeumaticoEnum.REPARACION_SALIDA,
                TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
                TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO # Necesita check adicional si fue a stock
            ]
            
            if evento.tipo_evento in eventos_a_stock and neumatico.estado_actual == EstadoNeumaticoEnum.EN_STOCK:
                # Asegurar que tenemos modelo_id y almacen_id, convertidos a UUID si son strings
                modelo_id = neumatico.modelo_id
                ubicacion_id = neumatico.ubicacion_almacen_id
                
                if modelo_id is not None and ubicacion_id is not None:
                    # Asegurar que sean objetos UUID para la consulta
                    if isinstance(modelo_id, str):
                        modelo_id = uuid.UUID(modelo_id)
                    if isinstance(ubicacion_id, str):
                        ubicacion_id = uuid.UUID(ubicacion_id)
                        
                    logger.debug(f"Evento {evento.tipo_evento} resultó en EN_STOCK. Verificando stock mínimo para M:{modelo_id} A:{ubicacion_id}")
                    await self._check_stock_minimo(modelo_id, ubicacion_id)
                else:
                    logger.warning(f"Faltan modelo_id o ubicacion_almacen_id para verificar stock mínimo tras evento {evento.tipo_evento} en neumático {neumatico_id_safe}")

            # 4. Verificar presión anormal (si el evento es una inspección con dato de presión)
            if evento.tipo_evento == TipoEventoNeumaticoEnum.INSPECCION and hasattr(evento, 'presion_psi') and evento.presion_psi is not None:
                await self._check_presion_anormal(neumatico, evento)
            
            # 5. Verificar fin de vida útil para cualquier tipo de evento
            # Es importante verificar regularmente, especialmente después de inspecciones o actualizaciones de km
            await self._check_fin_vida_util(neumatico)
            
            # 6. Añadir aquí llamadas a otras funciones de verificación de alertas

            logger.debug(f"Finalizado check_and_create_alerts para neumático {neumatico_id_safe}")
        except Exception as e:
            # Capturar cualquier error para evitar que interrumpa el flujo principal
            logger.error(f"Error al verificar alertas para neumático {getattr(neumatico, 'id', 'ID desconocido')}: {str(e)}", exc_info=True)
    
    async def _check_presion_anormal(self, neumatico: Neumatico, evento: EventoNeumatico):
        """Verificar si la presión reportada en un evento está fuera de los rangos aceptables."""
        if not hasattr(evento, 'presion_psi') or evento.presion_psi is None:
            return
        
        # Obtener modelo para conocer los parámetros de presión recomendada
        if neumatico.modelo_id is None:
            logger.warning(f"Neumático {neumatico.id} sin modelo asignado, no se puede verificar presión anormal")
            return
        
        modelo = await self.session.get(ModeloNeumatico, neumatico.modelo_id)
        if not modelo:
            logger.warning(f"Modelo {neumatico.modelo_id} no encontrado para verificar presión anormal")
            return
        
        # Si el modelo no tiene definida la presión recomendada, no podemos hacer la verificación
        if modelo.presion_recomendada_psi is None:
            logger.warning(f"Modelo {modelo.id} no tiene definida la presión recomendada, no se puede verificar presión anormal")
            return
        
        presion_recomendada = float(modelo.presion_recomendada_psi)
        presion_actual = float(evento.presion_psi)
        
        # Definir los umbrales de tolerancia (estos podrían configurarse desde parámetros de sistema)
        tolerancia_baja = 0.85  # 85% de la presión recomendada
        tolerancia_alta = 1.15  # 115% de la presión recomendada
        
        presion_minima = presion_recomendada * tolerancia_baja
        presion_maxima = presion_recomendada * tolerancia_alta
        
        # Verificar si la presión está por debajo del mínimo
        if presion_actual < presion_minima:
            # Preparar contexto para la alerta
            datos_contexto = {
                "presion_actual": presion_actual,
                "presion_recomendada": presion_recomendada,
                "presion_minima": presion_minima,
                "porcentaje_bajo": round((1 - (presion_actual / presion_recomendada)) * 100, 1),
                "modelo_nombre": modelo.nombre_modelo,
                "medida": modelo.medida,
                "numero_serie": neumatico.numero_serie,
                "descripcion_personalizada": f"El neumático {neumatico.numero_serie} tiene una presión de {presion_actual} PSI, que está por debajo del mínimo recomendado de {presion_minima} PSI. Presión recomendada: {presion_recomendada} PSI."
            }
            
            mensaje = f"Presión baja detectada: {presion_actual} PSI (mínimo recomendado: {presion_minima} PSI)"
            
            await self._crear_alerta_en_db(
                tipo_alerta=TipoAlertaEnum.PRESION_BAJA.value,
                mensaje=mensaje,
                nivel_severidad="WARN",
                neumatico_id=neumatico.id,
                modelo_id=neumatico.modelo_id,
                datos_contexto=datos_contexto
            )
        # Verificar si la presión está por encima del máximo
        elif presion_actual > presion_maxima:
            # Preparar contexto para la alerta
            datos_contexto = {
                "presion_actual": presion_actual,
                "presion_recomendada": presion_recomendada,
                "presion_maxima": presion_maxima,
                "porcentaje_alto": round(((presion_actual / presion_recomendada) - 1) * 100, 1),
                "modelo_nombre": modelo.nombre_modelo,
                "medida": modelo.medida,
                "numero_serie": neumatico.numero_serie,
                "descripcion_personalizada": f"El neumático {neumatico.numero_serie} tiene una presión de {presion_actual} PSI, que está por encima del máximo recomendado de {presion_maxima} PSI. Presión recomendada: {presion_recomendada} PSI."
            }
            
            mensaje = f"Presión alta detectada: {presion_actual} PSI (máximo recomendado: {presion_maxima} PSI)"
            
            await self._crear_alerta_en_db(
                tipo_alerta=TipoAlertaEnum.PRESION_ALTA.value,
                mensaje=mensaje,
                nivel_severidad="WARN",
                neumatico_id=neumatico.id,
                modelo_id=neumatico.modelo_id,
                datos_contexto=datos_contexto
            )
            
    async def _check_fin_vida_util(self, neumatico: Neumatico):
        """Verificar si un neumático ha alcanzado su fin de vida útil estimada."""
        # Obtener el modelo para conocer los parámetros de vida útil
        if neumatico.modelo_id is None:
            logger.warning(f"Neumático {neumatico.id} sin modelo asignado, no se puede verificar fin de vida útil")
            return
        
        modelo = await self.session.get(ModeloNeumatico, neumatico.modelo_id)
        if not modelo:
            logger.warning(f"Modelo {neumatico.modelo_id} no encontrado para verificar fin de vida útil")
            return
        
        # Comprobar si ya existe una alerta activa para este neumático
        query = select(Alerta).where(
            Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value, 
            Alerta.neumatico_id == neumatico.id,
            Alerta.resuelta == False
        )
        result = await self.session.exec(query)
        alerta_existente = result.first()
        if alerta_existente:
            # Ya existe una alerta, no crear otra
            return
        
        motivos_fin_vida = []
        razones = []
        
        # 1. Verificar edad máxima (en años)
        edad_maxima_anios = 7  # Valor predeterminado para la mayoría de neumáticos comerciales
        
        # Usar fecha de fabricación si está disponible, si no, usar fecha de compra
        fecha_inicio = neumatico.fecha_fabricacion if neumatico.fecha_fabricacion else neumatico.fecha_compra
        if fecha_inicio:
            # Calcular la edad actual en años
            hoy = datetime.now(timezone.utc).date()
            edad_anios = (hoy - fecha_inicio).days / 365.25  # Considerar años bisiestos
            
            if edad_anios >= edad_maxima_anios:
                motivos_fin_vida.append("EDAD_MAXIMA")
                razones.append(f"El neumático tiene {edad_anios:.1f} años, superando el máximo recomendado de {edad_maxima_anios} años.")
        
        # 2. Verificar kilometraje máximo
        km_maximo = 80000  # Valor predeterminado para la mayoría de neumáticos comerciales
        
        if neumatico.kilometraje_acumulado >= km_maximo:
            motivos_fin_vida.append("KILOMETRAJE_MAXIMO")
            razones.append(f"El neumático ha acumulado {neumatico.kilometraje_acumulado} km, superando el máximo recomendado de {km_maximo} km.")
        
        # Si se cumplió alguna de las condiciones, crear alerta
        if motivos_fin_vida:
            # Preparar contexto para la alerta
            datos_contexto = {
                "motivos": motivos_fin_vida,
                "razones": razones,
                "edad_anios": edad_anios if 'fecha_inicio' in locals() else None,
                "edad_maxima_anios": edad_maxima_anios,
                "kilometraje": neumatico.kilometraje_acumulado,
                "kilometraje_maximo": km_maximo,
                "fecha_compra": neumatico.fecha_compra.isoformat() if neumatico.fecha_compra else None,
                "fecha_fabricacion": neumatico.fecha_fabricacion.isoformat() if neumatico.fecha_fabricacion else None,
                "modelo_nombre": modelo.nombre_modelo,
                "medida": modelo.medida,
                "numero_serie": neumatico.numero_serie,
                "descripcion_personalizada": f"El neumático {neumatico.numero_serie} ha alcanzado su fin de vida útil estimada. {' '.join(razones)}"
            }
            
            mensaje = f"Fin de vida útil estimada: {', '.join(motivos_fin_vida)}"
            
            await self._crear_alerta_en_db(
                tipo_alerta=TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
                mensaje=mensaje,
                nivel_severidad="WARN",
                neumatico_id=neumatico.id,
                modelo_id=neumatico.modelo_id,
                datos_contexto=datos_contexto
            )
    # --- *** Fin Nuevo Método Público *** ---


    async def _check_desgaste_irregular(self, neumatico: Neumatico, evento: EventoNeumatico):
        """
        Verificar si hay patrones de desgaste irregular en el neumático según los datos 
        de la inspección. El desgaste irregular puede indicar problemas de alineación,
        balanceo, presión o suspensión.
        """
        # Solo proceder si es un evento de inspección y tiene datos de desgaste
        if evento.tipo_evento != TipoEventoNeumaticoEnum.INSPECCION:
            return
        
        # Verificar si ya existe una alerta activa de desgaste irregular para este neumático
        query = select(Alerta).where(
            Alerta.tipo_alerta == TipoAlertaEnum.DESGASTE_IRREGULAR.value,
            Alerta.neumatico_id == neumatico.id,
            Alerta.resuelta == False
        )
        result = await self.session.exec(query)
        alerta_existente = result.first()
        if alerta_existente:
            # Ya existe una alerta, no crear otra
            return
        
        # Indicadores de desgaste irregular
        indicadores_desgaste = []
        nivel_severidad = "INFO"
        
        # 1. Verificar diferencia significativa en profundidades (si se reportaron)
        if evento.profundidad_exterior_mm is not None and evento.profundidad_central_mm is not None and evento.profundidad_interior_mm is not None:
            # Calcular diferencia máxima entre las tres mediciones
            profundidades = [evento.profundidad_exterior_mm, evento.profundidad_central_mm, evento.profundidad_interior_mm]
            diferencia_max = max(profundidades) - min(profundidades)
            
            # Si la diferencia es mayor a 2mm, puede indicar desgaste irregular
            if diferencia_max >= 2:
                indicadores_desgaste.append("DESGASTE_DIFERENCIAL")
                detalle = f"Diferencia de {diferencia_max:.1f}mm entre las profundidades (ext:{evento.profundidad_exterior_mm}mm, cen:{evento.profundidad_central_mm}mm, int:{evento.profundidad_interior_mm}mm)"
                
                # Si la diferencia es muy grande (>4mm), aumentar severidad
                if diferencia_max >= 4:
                    nivel_severidad = "WARN"
        
        # 2. Verificar patrones específicos reportados en la inspección
        if evento.comentarios:
            patrones_desgaste = [
                ("desgaste lateral", "DESGASTE_LATERAL", "Desgaste excesivo en los bordes laterales, posible indicador de baja presión"),
                ("desgaste central", "DESGASTE_CENTRAL", "Desgaste excesivo en la zona central, posible indicador de sobrepresión"),
                ("desgaste irregular", "DESGASTE_IRREGULAR_GENERAL", "Patrón de desgaste irregular generalizado"),
                ("desgaste en parches", "DESGASTE_PARCHES", "Desgaste en forma de parches, posible indicador de problemas de suspensión"),
                ("desgaste aserrado", "DESGASTE_ASERRADO", "Patrón de desgaste en forma de sierra, posible indicador de problemas de alineación")
            ]
            
            for texto, codigo, descripcion in patrones_desgaste:
                if texto.lower() in evento.comentarios.lower():
                    indicadores_desgaste.append(codigo)
                    detalle = descripcion
                    nivel_severidad = "WARN"  # Estos patrones suelen ser más serios
        
        # 3. Verificar si se reportó desgaste anormal en algún campo específico
        if hasattr(evento, 'patron_desgaste') and evento.patron_desgaste:
            # Suponiendo que existe un campo patron_desgaste en el evento
            indicadores_desgaste.append(f"PATRON_{evento.patron_desgaste.upper()}")
            detalle = f"Patrón de desgaste anormal: {evento.patron_desgaste}"
            nivel_severidad = "WARN"
        
        # Si se detectó algún indicador de desgaste irregular, crear alerta
        if indicadores_desgaste:
            # Preparar contexto para la alerta
            datos_contexto = {
                "indicadores": indicadores_desgaste,
                "profundidad_exterior_mm": evento.profundidad_exterior_mm,
                "profundidad_central_mm": evento.profundidad_central_mm,
                "profundidad_interior_mm": evento.profundidad_interior_mm,
                "comentarios": evento.comentarios,
                "diferencia_profundidad": diferencia_max if 'diferencia_max' in locals() else None,
                "fecha_inspeccion": evento.fecha_evento.isoformat() if evento.fecha_evento else None,
                "inspector": evento.usuario_id,
                "numero_serie": neumatico.numero_serie,
                "posicion": safe_str_uuid(neumatico.ubicacion_actual_posicion_id) if neumatico.ubicacion_actual_posicion_id else None,
                "vehiculo": safe_str_uuid(neumatico.ubicacion_actual_vehiculo_id) if neumatico.ubicacion_actual_vehiculo_id else None,
                "detalle": detalle if 'detalle' in locals() else "Patrón de desgaste irregular detectado"
            }
            
            mensaje = f"Desgaste irregular detectado: {', '.join(indicadores_desgaste)}"
            
            await self._crear_alerta_en_db(
                tipo_alerta=TipoAlertaEnum.DESGASTE_IRREGULAR.value,
                mensaje=mensaje,
                nivel_severidad=nivel_severidad,
                neumatico_id=neumatico.id,
                modelo_id=neumatico.modelo_id,
                vehiculo_id=neumatico.ubicacion_actual_vehiculo_id,
                datos_contexto=datos_contexto
            )

# --- Fin del archivo ---