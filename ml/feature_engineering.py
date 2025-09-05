"""
Feature Engineering para Modelo Predictivo de Neumáticos
Sprint 2: Creación de características derivadas para ML
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class NeumaticoFeatureEngineer:
    """Clase para ingeniería de características de neumáticos."""
    
    def __init__(self):
        self.feature_names = []
        
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear características temporales."""
        df = df.copy()
        
        # Edad del neumático en días
        if 'fecha_compra' in df.columns:
            df['edad_dias'] = (datetime.now() - pd.to_datetime(df['fecha_compra'])).dt.days
            df['edad_meses'] = df['edad_dias'] / 30.44
            df['edad_anos'] = df['edad_dias'] / 365.25
        
        # Tiempo desde fabricación
        if 'fecha_fabricacion' in df.columns:
            df['tiempo_desde_fabricacion_dias'] = (
                datetime.now() - pd.to_datetime(df['fecha_fabricacion'])
            ).dt.days
        
        # Tiempo en servicio (si está instalado)
        if 'fecha_inicio_vida_actual' in df.columns:
            df['tiempo_servicio_actual_dias'] = (
                datetime.now() - pd.to_datetime(df['fecha_inicio_vida_actual'])
            ).dt.days
        
        return df
    
    def create_usage_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear características de uso."""
        df = df.copy()
        
        # Kilometraje por día
        if 'kilometraje_acumulado' in df.columns and 'edad_dias' in df.columns:
            df['km_por_dia'] = df['kilometraje_acumulado'] / (df['edad_dias'] + 1)
        
        # Kilometraje por vida actual
        if 'kilometraje_vida_actual' in df.columns and 'tiempo_servicio_actual_dias' in df.columns:
            df['km_por_dia_vida_actual'] = df['kilometraje_vida_actual'] / (df['tiempo_servicio_actual_dias'] + 1)
        
        # Intensidad de uso (categorías)
        if 'km_por_dia' in df.columns:
            df['intensidad_uso'] = pd.cut(
                df['km_por_dia'], 
                bins=[0, 50, 150, 300, float('inf')], 
                labels=['Bajo', 'Medio', 'Alto', 'Muy Alto']
            )
        
        return df
    
    def create_wear_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear características de desgaste."""
        df = df.copy()
        
        # Desgaste por kilómetro (real vs esperado)
        if all(col in df.columns for col in ['profundidad_original_mm', 'profundidad_remanente_actual_mm', 'kilometraje_acumulado']):
            df['desgaste_total_mm'] = df['profundidad_original_mm'] - df['profundidad_remanente_actual_mm']
            df['desgaste_por_km'] = df['desgaste_total_mm'] / (df['kilometraje_acumulado'] + 1)
        
        # Ratio de desgaste vs esperado
        if all(col in df.columns for col in ['desgaste_por_km', 'tasa_desgaste_esperada_mm_km']):
            df['ratio_desgaste_esperado'] = df['desgaste_por_km'] / (df['tasa_desgaste_esperada_mm_km'] + 0.0001)
        
        # Porcentaje de vida útil consumida
        if all(col in df.columns for col in ['profundidad_original_mm', 'profundidad_remanente_actual_mm']):
            df['porcentaje_vida_consumida'] = (
                (df['profundidad_original_mm'] - df['profundidad_remanente_actual_mm']) / 
                df['profundidad_original_mm'] * 100
            )
        
        return df
    
    def create_maintenance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear características de mantenimiento."""
        df = df.copy()
        
        # Número de reencauches realizados vs máximo
        if all(col in df.columns for col in ['reencauches_realizados', 'vida_actual']):
            df['reencauches_por_vida'] = df['reencauches_realizados'] / df['vida_actual']
        
        # Vida actual como porcentaje del máximo
        df['porcentaje_vida_maxima'] = (df['vida_actual'] / 11) * 100  # Máximo 11 vidas
        
        # Indicador de neumático reencauchado
        if 'es_reencauchado' in df.columns:
            df['es_reencauchado_num'] = df['es_reencauchado'].astype(int)
        
        return df
    
    def create_model_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear características del modelo de neumático."""
        df = df.copy()
        
        # Categorizar por medida (tamaño)
        if 'medida' in df.columns:
            # Extraer ancho de llanta (primer número)
            df['ancho_llanta'] = df['medida'].str.extract(r'(\d+)').astype(float)
            
            # Categorizar por tamaño
            df['categoria_tamano'] = pd.cut(
                df['ancho_llanta'], 
                bins=[0, 225, 275, 315, float('inf')], 
                labels=['Pequeño', 'Mediano', 'Grande', 'Extra Grande']
            )
        
        # Ratio vida útil teórica vs real
        if all(col in df.columns for col in ['vida_util_teorica_km', 'kilometraje_acumulado']):
            df['ratio_km_teorico'] = df['kilometraje_acumulado'] / (df['vida_util_teorica_km'] + 1)
        
        return df
    
    def create_target_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear variables objetivo para ML."""
        df = df.copy()
        
        # Variable objetivo: neumático próximo a reemplazo (binaria)
        if 'porcentaje_vida_consumida' in df.columns:
            df['necesita_reemplazo_pronto'] = (df['porcentaje_vida_consumida'] > 80).astype(int)
        
        # Variable objetivo: vida útil restante estimada
        if all(col in df.columns for col in ['vida_util_teorica_km', 'kilometraje_acumulado']):
            df['vida_util_restante_estimada'] = np.maximum(
                0, df['vida_util_teorica_km'] - df['kilometraje_acumulado']
            )
        
        # Días hasta reemplazo estimado (basado en desgaste actual)
        if all(col in df.columns for col in ['profundidad_remanente_actual_mm', 'desgaste_por_km', 'km_por_dia']):
            # Profundidad mínima para retiro: 1.6mm
            profundidad_minima = 1.6
            mm_restantes = np.maximum(0, df['profundidad_remanente_actual_mm'] - profundidad_minima)
            km_restantes = mm_restantes / (df['desgaste_por_km'] + 0.0001)
            df['dias_hasta_reemplazo'] = km_restantes / (df['km_por_dia'] + 0.1)
        
        return df
    
    def engineer_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar toda la ingeniería de características."""
        logger.info(f"Iniciando feature engineering para {len(df)} registros")
        
        # Aplicar todas las transformaciones
        df = self.create_temporal_features(df)
        df = self.create_usage_features(df)
        df = self.create_wear_features(df)
        df = self.create_maintenance_features(df)
        df = self.create_model_features(df)
        df = self.create_target_variables(df)
        
        # Guardar nombres de características creadas
        original_cols = [
            'neumatico_id', 'numero_serie', 'modelo_neumatico_id', 'medida',
            'profundidad_original_mm', 'tasa_desgaste_esperada_mm_km', 'vida_util_teorica_km',
            'fecha_compra', 'fecha_fabricacion', 'vida_actual', 'es_reencauchado',
            'kilometraje_acumulado', 'kilometraje_vida_actual', 'profundidad_remanente_actual_mm'
        ]
        
        self.feature_names = [col for col in df.columns if col not in original_cols]
        
        logger.info(f"Feature engineering completado. {len(self.feature_names)} características creadas")
        return df
    
    def get_ml_ready_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Preparar dataset final para ML."""
        # Seleccionar solo características numéricas para ML
        numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Excluir IDs y fechas
        exclude_cols = ['neumatico_id', 'modelo_neumatico_id']
        ml_features = [col for col in numeric_features if col not in exclude_cols]
        
        # Dataset final
        ml_df = df[ml_features].copy()
        
        # Manejar valores faltantes
        ml_df = ml_df.fillna(ml_df.median())
        
        return ml_df, ml_features


def main():
    """Función principal para testing."""
    # Ejemplo de uso
    engineer = NeumaticoFeatureEngineer()
    
    # Datos de ejemplo
    sample_data = {
        'neumatico_id': ['1', '2', '3'],
        'medida': ['295/80R22.5', '315/70R22.5', '275/80R22.5'],
        'profundidad_original_mm': [16.0, 18.0, 15.0],
        'profundidad_remanente_actual_mm': [12.0, 15.0, 8.0],
        'kilometraje_acumulado': [50000, 30000, 80000],
        'vida_util_teorica_km': [120000, 150000, 100000],
        'fecha_compra': ['2023-01-01', '2023-06-01', '2022-12-01'],
        'es_reencauchado': [False, False, True],
        'vida_actual': [1, 1, 2]
    }
    
    df = pd.DataFrame(sample_data)
    df['fecha_compra'] = pd.to_datetime(df['fecha_compra'])
    
    # Aplicar feature engineering
    df_engineered = engineer.engineer_all_features(df)
    
    print("Características creadas:")
    for feature in engineer.feature_names:
        print(f"- {feature}")
    
    return df_engineered


if __name__ == "__main__":
    result = main()
    print(result.head())
