"""
Script de Predicción Independiente para Neumáticos
Sprint 2: Predicciones usando modelo entrenado
"""
import joblib
import pandas as pd
import numpy as np
import json
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class NeumaticoPredictor:
    """Predictor independiente para vida útil de neumáticos."""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.metadata = {}
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Cargar modelo entrenado."""
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.scaler = model_data.get('scaler')
            self.feature_names = model_data['feature_names']
            self.metadata = model_data['metadata']
            
            logger.info(f"Modelo cargado: {self.metadata.get('model_type', 'unknown')}")
            logger.info(f"Características requeridas: {len(self.feature_names)}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise
    
    def predict_single(self, neumatico_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicción para un neumático individual."""
        if self.model is None:
            raise ValueError("Modelo no cargado")
        
        try:
            # Preparar características
            features = self._prepare_features(neumatico_data)
            
            # Realizar predicción
            if self.scaler:
                features_scaled = self.scaler.transform([features])
                prediction = self.model.predict(features_scaled)[0]
            else:
                prediction = self.model.predict([features])[0]
            
            # Calcular confianza (simplificada)
            confidence = self._calculate_confidence(features, prediction)
            
            # Calcular fecha estimada de reemplazo
            estimated_date = self._calculate_replacement_date(
                neumatico_data, prediction
            )
            
            result = {
                'neumatico_id': neumatico_data.get('neumatico_id'),
                'vida_util_restante_km': max(0, int(prediction)),
                'confianza_prediccion': round(confidence, 3),
                'fecha_estimada_reemplazo': estimated_date,
                'fecha_prediccion': datetime.now().isoformat(),
                'modelo_version': self.metadata.get('model_type', 'v1.0')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {
                'neumatico_id': neumatico_data.get('neumatico_id'),
                'error': str(e),
                'fecha_prediccion': datetime.now().isoformat()
            }
    
    def predict_batch(self, neumaticos_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predicciones para múltiples neumáticos."""
        results = []
        
        for neumatico_data in neumaticos_data:
            result = self.predict_single(neumatico_data)
            results.append(result)
        
        return results
    
    def _prepare_features(self, neumatico_data: Dict[str, Any]) -> List[float]:
        """Preparar características para predicción."""
        features = []
        
        for feature_name in self.feature_names:
            value = neumatico_data.get(feature_name, 0)
            
            # Manejar valores especiales
            if pd.isna(value) or value is None:
                value = 0
            
            features.append(float(value))
        
        return features
    
    def _calculate_confidence(self, features: List[float], prediction: float) -> float:
        """Calcular confianza de la predicción (simplificada)."""
        # Confianza basada en completitud de datos
        non_zero_features = sum(1 for f in features if f != 0)
        data_completeness = non_zero_features / len(features)
        
        # Confianza basada en rango de predicción
        if prediction < 0:
            range_confidence = 0.3
        elif prediction > 200000:  # Muy alto
            range_confidence = 0.5
        else:
            range_confidence = 0.8
        
        # Confianza combinada
        confidence = (data_completeness * 0.6) + (range_confidence * 0.4)
        return min(1.0, max(0.1, confidence))
    
    def _calculate_replacement_date(self, neumatico_data: Dict[str, Any], 
                                  vida_restante_km: float) -> Optional[str]:
        """Calcular fecha estimada de reemplazo."""
        try:
            km_por_dia = neumatico_data.get('km_por_dia', 0)
            
            if km_por_dia <= 0:
                return None
            
            dias_restantes = vida_restante_km / km_por_dia
            fecha_reemplazo = datetime.now() + pd.Timedelta(days=dias_restantes)
            
            return fecha_reemplazo.date().isoformat()
            
        except Exception:
            return None


def predict_from_json(json_input: str, model_path: str = 'ml/modelo_xgboost_v1.pkl') -> str:
    """Función principal para predicción desde JSON."""
    try:
        # Cargar datos
        if isinstance(json_input, str):
            data = json.loads(json_input)
        else:
            data = json_input
        
        # Inicializar predictor
        predictor = NeumaticoPredictor(model_path)
        
        # Realizar predicción
        if isinstance(data, list):
            results = predictor.predict_batch(data)
        else:
            results = predictor.predict_single(data)
        
        return json.dumps(results, indent=2, default=str)
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return json.dumps(error_result, indent=2)


def main():
    """Función principal para testing."""
    # Datos de ejemplo
    sample_neumatico = {
        'neumatico_id': 'test-001',
        'kilometraje_acumulado': 75000,
        'vida_actual': 2,
        'profundidad_remanente_actual_mm': 8.5,
        'edad_dias': 450,
        'km_por_dia': 167,
        'desgaste_por_km': 0.0045,
        'porcentaje_vida_consumida': 65.2,
        'ratio_desgaste_esperado': 1.2
    }
    
    # Crear modelo dummy para testing
    from sklearn.ensemble import RandomForestRegressor
    import joblib
    
    # Crear directorio si no existe
    Path('ml').mkdir(exist_ok=True)
    
    # Modelo dummy
    dummy_model = RandomForestRegressor(n_estimators=10, random_state=42)
    dummy_features = list(sample_neumatico.keys())[1:]  # Excluir ID
    dummy_X = np.random.rand(100, len(dummy_features))
    dummy_y = np.random.randint(0, 50000, 100)
    
    dummy_model.fit(dummy_X, dummy_y)
    
    # Guardar modelo dummy
    model_data = {
        'model': dummy_model,
        'scaler': None,
        'feature_names': dummy_features,
        'metadata': {
            'model_type': 'random_forest_dummy',
            'training_date': datetime.now().isoformat()
        }
    }
    
    joblib.dump(model_data, 'ml/modelo_dummy.pkl')
    
    # Probar predicción
    result = predict_from_json(json.dumps(sample_neumatico), 'ml/modelo_dummy.pkl')
    print("Resultado de predicción:")
    print(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
