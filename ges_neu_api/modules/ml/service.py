"""
Servicio ML para datos de entrenamiento y predicciones.
Sprint 1: Preparación de datos históricos.
Sprint 3: Integración de predicciones en tiempo real.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
import json
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from ...core.exceptions import RecursoNoEncontradoError, OperacionInvalidaError
from ..neumaticos.models import Neumatico, ModeloNeumatico, FabricanteNeumatico
from ..vehiculos.models import Vehiculos, PosicionesNeumatico
from .schemas import TrainingDataPoint, TrainingDataResponse, PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


class MLService:
    """Servicio para operaciones de Machine Learning."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_training_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_active: bool = True,
        include_inactive: bool = True,
        min_km: Optional[int] = None,
        max_km: Optional[int] = None
    ) -> TrainingDataResponse:
        """
        Obtiene datos históricos de neumáticos para entrenamiento ML.
        
        Args:
            start_date: Fecha inicio del rango (fecha_compra)
            end_date: Fecha fin del rango (fecha_compra)
            include_active: Incluir neumáticos activos
            include_inactive: Incluir neumáticos inactivos/desechados
            min_km: Kilometraje mínimo acumulado
            max_km: Kilometraje máximo acumulado
        """
        
        # Construir query base con joins necesarios
        query = (
            select(Neumatico, ModeloNeumatico, FabricanteNeumatico)
            .join(ModeloNeumatico, Neumatico.modelo_id == ModeloNeumatico.id)
            .join(FabricanteNeumatico, ModeloNeumatico.fabricante_id == FabricanteNeumatico.id)
        )
        
        # Aplicar filtros
        conditions = []
        
        if start_date:
            conditions.append(Neumatico.fecha_compra >= start_date)
        if end_date:
            conditions.append(Neumatico.fecha_compra <= end_date)
            
        if not include_active and not include_inactive:
            raise OperacionInvalidaError("Debe incluir al menos neumáticos activos o inactivos")
        elif include_active and not include_inactive:
            conditions.append(Neumatico.activo == True)
        elif not include_active and include_inactive:
            conditions.append(Neumatico.activo == False)
        # Si ambos son True, no agregamos filtro de activo
        
        if min_km is not None:
            conditions.append(Neumatico.kilometraje_acumulado >= min_km)
        if max_km is not None:
            conditions.append(Neumatico.kilometraje_acumulado <= max_km)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Ordenar por fecha de compra para consistencia
        query = query.order_by(Neumatico.fecha_compra.desc())
        
        # Ejecutar query
        result = await self.db.execute(query)
        rows = result.all()
        
        # Procesar datos
        data_points = []
        for neumatico, modelo, fabricante in rows:
            data_point = TrainingDataPoint(
                neumatico_id=neumatico.id,
                numero_serie=neumatico.numero_serie,
                modelo_neumatico_id=neumatico.modelo_id,
                
                # Datos del modelo
                medida=modelo.medida,
                profundidad_original_mm=modelo.profundidad_original_mm,
                tasa_desgaste_esperada_mm_km=modelo.tasa_desgaste_esperada_mm_km,
                vida_util_teorica_km=modelo.vida_util_teorica_km,
                
                # Datos del neumático
                fecha_compra=neumatico.fecha_compra,
                fecha_fabricacion=neumatico.fecha_fabricacion,
                vida_actual=neumatico.vida_actual,
                es_reencauchado=neumatico.es_reencauchado,
                kilometraje_acumulado=neumatico.kilometraje_acumulado,
                kilometraje_vida_actual=neumatico.kilometraje_vida_actual,
                
                # Mediciones actuales
                profundidad_remanente_actual_mm=neumatico.profundidad_remanente_actual_mm,
                fecha_ultima_medicion_profundidad=neumatico.fecha_ultima_medicion_profundidad,
                tasa_desgaste_actual_mm_km=neumatico.tasa_desgaste_actual_mm_km,
                
                # Ubicación y uso
                ubicacion_actual_vehiculo_id=neumatico.ubicacion_actual_vehiculo_id,
                ubicacion_actual_posicion_id=neumatico.ubicacion_actual_posicion_id,
                
                # Variables objetivo
                vida_util_restante_km=neumatico.vida_util_restante_km,
                fecha_desecho=neumatico.fecha_desecho
            )
            data_points.append(data_point)
        
        # Calcular estadísticas resumen
        total_records = len(data_points)
        
        if total_records > 0:
            fechas_compra = [dp.fecha_compra for dp in data_points if dp.fecha_compra]
            date_range = {
                "start": min(fechas_compra) if fechas_compra else None,
                "end": max(fechas_compra) if fechas_compra else None
            }
            
            # Estadísticas básicas
            km_values = [dp.kilometraje_acumulado for dp in data_points]
            profundidades = [dp.profundidad_remanente_actual_mm for dp in data_points if dp.profundidad_remanente_actual_mm]
            
            summary_stats = {
                "total_neumaticos": total_records,
                "km_promedio": sum(km_values) / len(km_values) if km_values else 0,
                "km_min": min(km_values) if km_values else 0,
                "km_max": max(km_values) if km_values else 0,
                "profundidad_promedio": float(sum(profundidades) / len(profundidades)) if profundidades else 0,
                "neumaticos_con_medicion": len(profundidades),
                "neumaticos_reencauchados": sum(1 for dp in data_points if dp.es_reencauchado),
                "neumaticos_desechados": sum(1 for dp in data_points if dp.fecha_desecho),
                "vidas_promedio": sum(dp.vida_actual for dp in data_points) / total_records
            }
        else:
            date_range = {"start": None, "end": None}
            summary_stats = {}
        
        return TrainingDataResponse(
            total_records=total_records,
            data_points=data_points,
            date_range=date_range,
            summary_stats=summary_stats
        )
    
    async def get_neumaticos_for_prediction(
        self,
        only_active: bool = True,
        neumatico_ids: Optional[List[UUID]] = None
    ) -> List[Neumatico]:
        """
        Obtiene neumáticos candidatos para predicción.
        
        Args:
            only_active: Solo neumáticos activos
            neumatico_ids: IDs específicos a procesar
        """
        query = select(Neumatico)
        
        conditions = []
        
        if only_active:
            conditions.append(Neumatico.activo == True)
            conditions.append(Neumatico.estado_actual.in_(['INSTALADO', 'EN_STOCK']))
        
        if neumatico_ids:
            conditions.append(Neumatico.id.in_(neumatico_ids))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_prediction_fields(
        self,
        neumatico_id: UUID,
        vida_util_restante_km: Optional[int],
        prediccion_fecha_reemplazo: Optional[date],
        confianza_prediccion: Optional[Decimal],
        modelo_version: str
    ) -> bool:
        """
        Actualiza los campos de predicción de un neumático.
        
        Args:
            neumatico_id: ID del neumático
            vida_util_restante_km: Vida útil restante predicha
            prediccion_fecha_reemplazo: Fecha predicha de reemplazo
            confianza_prediccion: Confianza de la predicción (0.0-1.0)
            modelo_version: Versión del modelo ML utilizado
        """
        result = await self.db.execute(
            select(Neumatico).where(Neumatico.id == neumatico_id)
        )
        neumatico = result.scalar_one_or_none()
        
        if not neumatico:
            raise RecursoNoEncontradoError("Neumático", str(neumatico_id))
        
        # Actualizar campos de predicción
        neumatico.vida_util_restante_km = vida_util_restante_km
        neumatico.prediccion_fecha_reemplazo = prediccion_fecha_reemplazo
        neumatico.confianza_prediccion = confianza_prediccion
        neumatico.fecha_ultima_prediccion = datetime.utcnow()
        neumatico.modelo_prediccion_version = modelo_version
        
        await self.db.commit()
        return True
    
    async def predict_single_neumatico(self, neumatico_id: UUID) -> PredictionResponse:
        """
        Realizar predicción para un neumático específico.
        
        Args:
            neumatico_id: ID del neumático a predecir
        """
        # Obtener datos del neumático
        result = await self.db.execute(
            select(Neumatico, ModeloNeumatico, FabricanteNeumatico)
            .join(ModeloNeumatico, Neumatico.modelo_id == ModeloNeumatico.id)
            .join(FabricanteNeumatico, ModeloNeumatico.fabricante_id == FabricanteNeumatico.id)
            .where(Neumatico.id == neumatico_id)
        )
        row = result.first()
        
        if not row:
            raise RecursoNoEncontradoError("Neumático", str(neumatico_id))
        
        neumatico, modelo, fabricante = row
        
        # Preparar datos para predicción
        prediction_data = self._prepare_prediction_data(neumatico, modelo)
        
        # Llamar al predictor independiente
        try:
            from ....ml.predict import predict_from_json
            
            # Usar modelo por defecto si existe
            model_path = Path("ml/modelo_xgboost_v1.pkl")
            if not model_path.exists():
                model_path = Path("ml/modelo_random_forest_v1.pkl")
            
            if not model_path.exists():
                raise OperacionInvalidaError("No hay modelos entrenados disponibles")
            
            # Realizar predicción
            result_json = predict_from_json(json.dumps(prediction_data), str(model_path))
            result_dict = json.loads(result_json)
            
            if "error" in result_dict:
                raise OperacionInvalidaError(f"Error en predicción: {result_dict['error']}")
            
            # Actualizar campos en BD
            await self.update_prediction_fields(
                neumatico_id=neumatico_id,
                vida_util_restante_km=result_dict.get('vida_util_restante_km'),
                prediccion_fecha_reemplazo=datetime.fromisoformat(result_dict['fecha_estimada_reemplazo']).date() if result_dict.get('fecha_estimada_reemplazo') else None,
                confianza_prediccion=Decimal(str(result_dict.get('confianza_prediccion', 0.5))),
                modelo_version=result_dict.get('modelo_version', 'v1.0')
            )
            
            return PredictionResponse(
                neumatico_id=neumatico_id,
                vida_util_restante_km=result_dict.get('vida_util_restante_km'),
                confianza_prediccion=result_dict.get('confianza_prediccion'),
                fecha_estimada_reemplazo=result_dict.get('fecha_estimada_reemplazo'),
                modelo_version=result_dict.get('modelo_version'),
                fecha_prediccion=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error en predicción para neumático {neumatico_id}: {e}")
            raise OperacionInvalidaError(f"Error en predicción: {str(e)}")
    
    async def recalculate_all_predictions(self, only_active: bool = True) -> Dict[str, Any]:
        """
        Recalcular predicciones para todos los neumáticos.
        
        Args:
            only_active: Solo recalcular neumáticos activos
        """
        # Obtener neumáticos candidatos
        neumaticos = await self.get_neumaticos_for_prediction(only_active=only_active)
        
        results = {
            "total_processed": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "errors": []
        }
        
        for neumatico in neumaticos:
            try:
                await self.predict_single_neumatico(neumatico.id)
                results["successful_predictions"] += 1
            except Exception as e:
                results["failed_predictions"] += 1
                results["errors"].append({
                    "neumatico_id": str(neumatico.id),
                    "error": str(e)
                })
            
            results["total_processed"] += 1
        
        logger.info(f"Recálculo completado: {results['successful_predictions']}/{results['total_processed']} exitosos")
        return results
    
    def _prepare_prediction_data(self, neumatico: Neumatico, modelo: ModeloNeumatico) -> Dict[str, Any]:
        """
        Preparar datos del neumático para predicción.
        """
        # Calcular edad en días
        edad_dias = 0
        if neumatico.fecha_fabricacion:
            edad_dias = (datetime.now().date() - neumatico.fecha_fabricacion).days
        elif neumatico.fecha_compra:
            edad_dias = (datetime.now().date() - neumatico.fecha_compra).days
        
        # Calcular km por día
        km_por_dia = 0
        if edad_dias > 0 and neumatico.kilometraje_acumulado:
            km_por_dia = neumatico.kilometraje_acumulado / edad_dias
        
        # Calcular desgaste por km
        desgaste_por_km = 0
        if neumatico.tasa_desgaste_actual_mm_km:
            desgaste_por_km = float(neumatico.tasa_desgaste_actual_mm_km)
        elif modelo.tasa_desgaste_esperada_mm_km and neumatico.kilometraje_vida_actual:
            desgaste_por_km = float(modelo.tasa_desgaste_esperada_mm_km)
        
        return {
            "neumatico_id": str(neumatico.id),
            "kilometraje_acumulado": neumatico.kilometraje_acumulado or 0,
            "vida_actual": neumatico.vida_actual or 1,
            "profundidad_remanente_actual_mm": float(neumatico.profundidad_remanente_actual_mm or 0),
            "edad_dias": edad_dias,
            "km_por_dia": km_por_dia,
            "desgaste_por_km": desgaste_por_km,
            "es_reencauchado": neumatico.es_reencauchado or False,
            "kilometraje_vida_actual": neumatico.kilometraje_vida_actual or 0,
            "profundidad_original_mm": float(modelo.profundidad_original_mm or 16),
            "vida_util_teorica_km": modelo.vida_util_teorica_km or 100000
        }
