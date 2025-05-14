# services/alert_service.py (Versión mejorada)
import uuid
import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
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
from models.neumatico import EstadoNeumaticoEnum
from models.parametro_inventario import TipoParametroEnum
from models.evento_neumatico import TipoEventoNeumaticoEnum
from schemas.common import TipoAlertaEnum, SeveridadAlerta
from schemas.alerta import AlertaCreate, AlertaRead
from services.notification_service import NotificationService
from crud.crud_alerta import alerta as crud_alerta

logger = logging.getLogger(__name__)

# Resto de las funciones auxiliares...

class AlertService:
    def __init__(self, session: AsyncSession, bg_tasks=None):
        self.session = session
        self.notifier = NotificationService(bg_tasks)

    async def _crear_alerta(
        self,
        neumatico: Neumatico,
        tipo: str,
        severidad: str,
        descripcion: str,
        datos_contexto: Optional[Dict[str, Any]] = None,
        vehiculo_id: Optional[uuid.UUID] = None,
        modelo_id: Optional[uuid.UUID] = None,
        almacen_id: Optional[uuid.UUID] = None,
        parametro_id: Optional[uuid.UUID] = None
    ) -> Alerta:
        """
        Crea una nueva alerta en el sistema.
        
        Args:
            neumatico: Neumático asociado a la alerta
            tipo: Tipo de alerta (ver TipoAlertaEnum)
            severidad: Nivel de severidad (ver SeveridadAlerta)
            descripcion: Descripción detallada de la alerta
            datos_contexto: Datos adicionales relevantes para la alerta
            vehiculo_id: ID del vehículo relacionado (opcional)
            modelo_id: ID del modelo relacionado (opcional)
            almacen_id: ID del almacén relacionado (opcional)
            parametro_id: ID del parámetro relacionado (opcional)
            
        Returns:
            Alerta: La alerta creada
        """
        # Asegurarse de que los UUIDs se conviertan a strings para el contexto JSON
        datos_contexto = safe_dict_uuid_to_str(datos_contexto or {})
        
        alerta = Alerta(
            tipo_alerta=tipo,
            descripcion=descripcion,
            nivel_severidad=severidad,
            resuelta=False,
            notas_resolucion=None,
            neumatico_id=safe_uuid(neumatico.id),
            vehiculo_id=safe_uuid(vehiculo_id),
            modelo_id=safe_uuid(modelo_id or neumatico.modelo_id),
            almacen_id=safe_uuid(almacen_id),
            parametro_id=safe_uuid(parametro_id),
            datos_contexto=datos_contexto,
            creado_por=safe_uuid(neumatico.creado_por) if hasattr(neumatico, 'creado_por') else None,
            actualizado_por=safe_uuid(neumatico.actualizado_por) if hasattr(neumatico, 'actualizado_por') else None
        )
        
        self.session.add(alerta)
        await self.session.commit()
        await self.session.refresh(alerta)
        
        logger.info(f"Alerta creada: {alerta.id} - {tipo} - {severidad}")
        return alerta

    async def _create_alert(self, **kwargs):
        # Remove tipo_alerta from kwargs if it exists to avoid duplication
        tipo_alerta = kwargs.pop('tipo_alerta', TipoAlertaEnum.LIMITE_REENCAUCHES)
        descripcion = kwargs.pop('descripcion', 'Límite de reencauches alcanzado')
        alerta = AlertaCreate(tipo_alerta=tipo_alerta, descripcion=descripcion, **kwargs)
        db_alerta = await crud_alerta.create(self.session, obj_in=alerta)
        self.notifier.enqueue_alert_notification(db_alerta)
        return db_alerta

    async def _check_fin_vida_util(self, neumatico: Neumatico, evento: Optional[EventoNeumatico] = None) -> Optional[Alerta]:
        """
        Verifica si un neumático ha alcanzado su fin de vida útil estimada basado en:
        - Desgaste actual (si se proporciona evento con medición)
        - Edad del neumático
        - Kilometraje acumulado
        """
        if neumatico.modelo_id is None:
            logger.warning(f"Neumático {neumatico.id} sin modelo asignado")
            return None
            
        modelo = await self.session.get(ModeloNeumatico, neumatico.modelo_id)
        if not modelo:
            logger.warning(f"Modelo {neumatico.modelo_id} no encontrado")
            return None

        # Verificación por profundidad mínima (si hay evento con medición)
        if evento and evento.profundidad_remanente_mm is not None and modelo.profundidad_original_mm:
            # Obtener el umbral mínimo de profundidad del modelo o usar un valor por defecto
            umbral_minimo = float(getattr(modelo, 'profundidad_minima_mm', 5.0))
            prof_remanente = float(evento.profundidad_remanente_mm)
            
            if prof_remanente < umbral_minimo:
                alerta = await self._crear_alerta(
                    neumatico=neumatico,
                    tipo=TipoAlertaEnum.PROFUNDIDAD_BAJA.value,
                    severidad=SeveridadAlerta.WARN,
                    descripcion=f"Profundidad del dibujo ({prof_remanente}mm) por debajo del mínimo recomendado ({umbral_minimo}mm)",
                    datos_contexto={
                        "profundidad_actual": prof_remanente,
                        "profundidad_minima": umbral_minimo,
                        "unidad": "mm"
                    }
                )
                await self.session.commit()
                return alerta

        # Verificación por edad (7 años máximo)
        fecha_inicio = neumatico.fecha_fabricacion or neumatico.fecha_compra
        if fecha_inicio:
            edad_anios = (datetime.now(timezone.utc).date() - fecha_inicio).days / 365.25
            if edad_anios >= 7:
                return await self._crear_alerta(
                    neumatico=neumatico,
                    tipo=TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
                    severidad=SeveridadAlerta.WARN,
                    descripcion=f"Edad del neumático: {edad_anios:.1f} años, superando el máximo recomendado",
                    datos_contexto={
                        "tipo": "EDAD",
                        "motivos": ["EDAD_MAXIMA"],
                        "edad_actual": round(edad_anios, 1),
                        "edad_maxima": 7,
                        "unidad": "años",
                        "fecha_inicio": fecha_inicio.isoformat()
                    }
                )

        # Verificación por kilometraje (80,000 km máximo)
        if neumatico.kilometraje_acumulado >= 80000:
            return await self._crear_alerta(
                neumatico=neumatico,
                tipo=TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
                severidad=SeveridadAlerta.WARN,
                descripcion=f"Kilometraje del neumático: {neumatico.kilometraje_acumulado} km, superando el máximo recomendado",
                datos_contexto={
                    "tipo": "KILOMETRAJE",
                    "motivos": ["KILOMETRAJE_MAXIMO"],
                    "km_actual": neumatico.kilometraje_acumulado,
                    "km_maximo": 80000,
                    "unidad": "km"
                }
            )

        return None

    async def _check_limite_reencauches(self, neumatico: Neumatico) -> Optional[Alerta]:
        """
        Verifica si un neumático ha alcanzado el límite de reencauches permitidos.
        """
        if neumatico.modelo_id is None:
            logger.warning(f"Neumático {neumatico.id} sin modelo asignado")
            return None
            
        modelo = await self.session.get(ModeloNeumatico, neumatico.modelo_id)
        if not modelo:
            logger.warning(f"Modelo {neumatico.modelo_id} no encontrado")
            return None
            
        # Si el modelo no permite reencauche, no hay alerta que generar
        if not modelo.permite_reencauche:
            return None
            
        # Si no se especifica un límite de reencauches, usar un valor por defecto
        reencauches_maximos = modelo.reencauches_maximos or 2
        
        if neumatico.reencauches_realizados >= reencauches_maximos:
            alerta = await self._crear_alerta(
                neumatico=neumatico,
                tipo=TipoAlertaEnum.LIMITE_REENCAUCHES,
                severidad=SeveridadAlerta.WARN,
                descripcion=f"Se ha alcanzado el límite de {reencauches_maximos} reencauche{'s' if reencauches_maximos > 1 else ''} permitido{'s' if reencauches_maximos > 1 else ''}.",
                datos_contexto={
                    "reencauches_realizados": neumatico.reencauches_realizados,
                    "reencauches_maximos": reencauches_maximos,
                    "motivos": ["LIMITE_REENCAUCHES"]
                }
            )
            await self.session.commit()
            return alerta
        
        return None

    async def _check_presion_anormal(
        self, 
        neumatico: Neumatico, 
        evento: EventoNeumatico
    ) -> Optional[Alerta]:
        """
        Verifica si la presión del neumático está fuera de los rangos normales.
        """
        # Solo verificar presión en eventos de inspección o instalación
        if evento.tipo_evento not in [
            TipoEventoNeumaticoEnum.INSPECCION.value,
            TipoEventoNeumaticoEnum.INSTALACION.value
        ]:
            return None
            
        if evento.presion_psi is None:
            return None
            
        if neumatico.modelo_id is None:
            logger.warning(f"Neumático {neumatico.id} sin modelo asignado")
            return None
            
        modelo = await self.session.get(ModeloNeumatico, neumatico.modelo_id)
        if not modelo or not modelo.presion_recomendada_psi:
            return None
            
        presion_recomendada = modelo.presion_recomendada_psi
        presion_actual = evento.presion_psi
        
        # Umbrales de presión (85% y 115% de la presión recomendada)
        umbral_bajo = presion_recomendada * 0.85
        umbral_alto = presion_recomendada * 1.15
        
        if presion_actual < umbral_bajo:
            return await self._crear_alerta(
                neumatico=neumatico,
                tipo=TipoAlertaEnum.PRESION_BAJA.value,
                severidad=SeveridadAlerta.WARN,
                descripcion=f"Presión de {presion_actual} psi está por debajo del mínimo recomendado",
                datos_contexto={
                    "tipo": "PRESION_BAJA",
                    "presion_actual": presion_actual,
                    "presion_recomendada": presion_recomendada,
                    "umbral": umbral_bajo,
                    "unidad": "psi",
                    "motivos": ["PRESION_BAJA"]
                }
            )
        elif presion_actual > umbral_alto:
            return await self._crear_alerta(
                neumatico=neumatico,
                tipo=TipoAlertaEnum.PRESION_ALTA.value,
                severidad=SeveridadAlerta.WARN,
                descripcion=f"Presión de {presion_actual} psi está por encima del máximo recomendado",
                datos_contexto={
                    "tipo": "PRESION_ALTA",
                    "presion_actual": presion_actual,
                    "presion_recomendada": presion_recomendada,
                    "umbral": umbral_alto,
                    "unidad": "psi",
                    "motivos": ["PRESION_ALTA"]
                }
            )
            
        return None

    async def _check_desgaste_irregular(
        self, 
        neumatico: Neumatico, 
        evento: EventoNeumatico
    ) -> Optional[Alerta]:
        """
        Verifica si hay desgaste irregular en el neumático basado en los comentarios de inspección
        o mediciones de desgaste desigual.
        """
        # Solo verificar en eventos de inspección
        if evento.tipo_evento != TipoEventoNeumaticoEnum.INSPECCION.value:
            return None
            
        motivos = []
        
        # Verificar comentarios de inspección
        if evento.notas:
            # Palabras clave que indican desgaste irregular
            palabras_clave = [
                "desgaste irregular", "desgaste desigual", "desgaste en hombros",
                "desgaste central", "desgaste en bandas", "desgaste en hombro interno",
                "desgaste en hombro externo", "plano", "escalonado", "dientes de sierra"
            ]
            
            # Convertir comentarios a minúsculas para búsqueda insensible a mayúsculas
            comentarios = evento.notas.lower()
            
            # Buscar palabras clave en los comentarios
            motivos_comentarios = [
                palabra for palabra in palabras_clave 
                if palabra in comentarios
            ]
            motivos.extend(motivos_comentarios)
        
        # Verificar mediciones de desgaste desigual si están disponibles
        if hasattr(evento, 'profundidad_banda_izq') and hasattr(evento, 'profundidad_banda_der'):
            if evento.profundidad_banda_izq is not None and evento.profundidad_banda_der is not None:
                diferencia = abs(float(evento.profundidad_banda_izq) - float(evento.profundidad_banda_der))
                if diferencia > 2.0:  # Más de 2mm de diferencia entre bandas
                    motivos.append(f"diferencia de {diferencia:.1f}mm entre bandas")
        
        if hasattr(evento, 'profundidad_centro') and hasattr(evento, 'profundidad_banda_izq') and hasattr(evento, 'profundidad_banda_der'):
            if (evento.profundidad_centro is not None and 
                evento.profundidad_banda_izq is not None and 
                evento.profundidad_banda_der is not None):
                # Calcular diferencia entre centro y promedio de bandas
                prof_bandas = (float(evento.profundidad_banda_izq) + float(evento.profundidad_banda_der)) / 2
                diferencia_centro_bandas = abs(float(evento.profundidad_centro) - prof_bandas)
                if diferencia_centro_bandas > 1.5:  # Más de 1.5mm de diferencia
                    motivos.append(f"diferencia de {diferencia_centro_bandas:.1f}mm entre centro y bandas")
        
        if motivos:
            alerta = await self._crear_alerta(
                neumatico=neumatico,
                tipo=TipoAlertaEnum.DESGASTE_IRREGULAR.value,
                severidad=SeveridadAlerta.WARN,
                descripcion=f"Desgaste irregular detectado: {', '.join(motivos[:3])}",
                datos_contexto={
                    "tipo": "DESGASTE_IRREGULAR",
                    "motivos": motivos[:5],
                    "comentarios": evento.notas if hasattr(evento, 'notas') else None
                }
            )
            await self.session.commit()
            return alerta
            
        return None

    async def check_and_create_alerts(self, neumatico: Neumatico, evento: EventoNeumatico) -> List[Alerta]:
        alertas = []
        
        # Verificaciones que requieren el evento
        if alerta := await self._check_desgaste_irregular(neumatico, evento):
            alertas.append(alerta)
            
        if alerta := await self._check_presion_anormal(neumatico, evento):
            alertas.append(alerta)
            
        # Verificación de fin de vida útil (con evento para desgaste)
        if alerta := await self._check_fin_vida_util(neumatico, evento):
            alertas.append(alerta)
            
        # Verificación de límite de reencauches (no requiere evento)
        if alerta := await self._check_limite_reencauches(neumatico):
            alertas.append(alerta)
            
        return alertas

    async def check_profundidad(self, neumatico_id: uuid.UUID):
        # Get the tire
        statement = select(Neumatico).where(Neumatico.id == neumatico_id)
        result = await self.session.exec(statement)
        neumatico = result.one()
        
        # Get the minimum depth parameter for this tire model
        statement = select(ParametroInventario).where(
            ParametroInventario.modelo_id == neumatico.modelo_id,
            ParametroInventario.tipo_parametro == 'PROFUNDIDAD_MINIMA'
        )
        result = await self.session.exec(statement)
        parametro = result.first()
        
        if not parametro or not parametro.valor_numerico:
            return  # No depth parameter set for this model
            
        # Get the latest inspection event for this tire
        statement = select(EventoNeumatico).where(
            EventoNeumatico.neumatico_id == neumatico_id,
            EventoNeumatico.tipo_evento == TipoEventoNeumaticoEnum.INSPECCION.value
        ).order_by(EventoNeumatico.timestamp_evento.desc()).limit(1)
        
        result = await self.session.exec(statement)
        ultima_inspeccion = result.first()
        
        if not ultima_inspeccion or not ultima_inspeccion.profundidad_remanente_mm:
            return  # No inspection with depth measurement found
            
        # Check if the depth is below the minimum
        if ultima_inspeccion.profundidad_remanente_mm < parametro.valor_numerico:
            await self._create_alert(
                neumatico_id=neumatico_id,
                tipo_alerta=TipoAlertaEnum.PROFUNDIDAD_BAJA,
                descripcion=f'Profundidad {ultima_inspeccion.profundidad_remanente_mm}mm < {parametro.valor_numerico}mm',
                nivel_severidad=SeveridadAlerta.WARN,
                datos_contexto={
                    'profundidad_actual': ultima_inspeccion.profundidad_remanente_mm,
                    'profundidad_minima': parametro.valor_numerico,
                    'fecha_ultima_inspeccion': ultima_inspeccion.timestamp_evento.isoformat()
                }
            )

    async def check_reencauches(self, neumatico_id: uuid.UUID):
        statement = select(Neumatico).where(Neumatico.id == neumatico_id)
        result = await self.session.exec(statement)
        neumatico = result.one()
        if neumatico.modelo and neumatico.reencauches_realizados >= neumatico.modelo.reencauches_maximos:
            await self._create_alert(
                neumatico_id=neumatico_id,
                tipo_alerta=TipoAlertaEnum.LIMITE_REENCAUCHES,
                descripcion=f'Alcanzado límite de {neumatico.modelo.reencauches_maximos} reencauches',
                nivel_severidad=SeveridadAlerta.WARN,
                datos_contexto={
                    'reencauches_realizados': neumatico.reencauches_realizados,
                    'reencauches_maximos': neumatico.modelo.reencauches_maximos
                }
            )

    async def _get_neumatico(self, neumatico_id):
        statement = select(Neumatico).where(Neumatico.id == neumatico_id)
        result = await self.session.exec(statement)
        return result.one()

    async def _get_parametro(self, modelo_id, tipo_param):
        statement = select(ParametroInventario).where(ParametroInventario.modelo_id == modelo_id).where(ParametroInventario.tipo_parametro == tipo_param)
        result = await self.session.exec(statement)
        parametro = result.one()
        return parametro
