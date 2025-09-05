"""
Entrenamiento de Modelo Predictivo para Neumáticos
Sprint 2: XGBoost/RandomForest para predicción de vida útil
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import json
from datetime import datetime
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class NeumaticoPredictor:
    """Modelo predictivo para vida útil de neumáticos."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_metadata = {}
        
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'vida_util_restante_km') -> Tuple[np.ndarray, np.ndarray, list]:
        """Preparar datos para entrenamiento."""
        # Seleccionar características numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Excluir target y IDs
        exclude_cols = [target_col, 'neumatico_id', 'modelo_neumatico_id']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Filtrar registros con target válido
        valid_mask = df[target_col].notna() & (df[target_col] >= 0)
        df_clean = df[valid_mask].copy()
        
        X = df_clean[feature_cols].fillna(df_clean[feature_cols].median())
        y = df_clean[target_col]
        
        logger.info(f"Dataset preparado: {X.shape[0]} muestras, {X.shape[1]} características")
        return X.values, y.values, feature_cols
    
    def train_xgboost(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Entrenar modelo XGBoost."""
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar características
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Configurar XGBoost
        xgb_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        # Entrenar modelo
        self.model = xgb.XGBRegressor(**xgb_params)
        self.model.fit(X_train_scaled, y_train)
        
        # Predicciones
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Métricas
        metrics = {
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        logger.info(f"XGBoost entrenado - Test R²: {metrics['test_r2']:.3f}, Test MAE: {metrics['test_mae']:.0f}")
        return metrics
    
    def train_random_forest(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Entrenar modelo Random Forest."""
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Configurar Random Forest
        rf_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        }
        
        # Entrenar modelo
        self.model = RandomForestRegressor(**rf_params)
        self.model.fit(X_train, y_train)
        
        # Predicciones
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        # Métricas
        metrics = {
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        logger.info(f"Random Forest entrenado - Test R²: {metrics['test_r2']:.3f}, Test MAE: {metrics['test_mae']:.0f}")
        return metrics
    
    def optimize_hyperparameters(self, X: np.ndarray, y: np.ndarray, model_type: str = 'xgboost') -> Dict[str, Any]:
        """Optimizar hiperparámetros con Grid Search."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        if model_type == 'xgboost':
            # Escalar para XGBoost
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            model = xgb.XGBRegressor(random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [4, 6, 8],
                'learning_rate': [0.05, 0.1, 0.15]
            }
            
            grid_search = GridSearchCV(model, param_grid, cv=3, scoring='neg_mean_absolute_error', n_jobs=-1)
            grid_search.fit(X_train_scaled, y_train)
            
            self.model = grid_search.best_estimator_
            y_pred = self.model.predict(X_test_scaled)
            
        else:  # Random Forest
            model = RandomForestRegressor(random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [8, 10, 12],
                'min_samples_split': [2, 5, 10]
            }
            
            grid_search = GridSearchCV(model, param_grid, cv=3, scoring='neg_mean_absolute_error', n_jobs=-1)
            grid_search.fit(X_train, y_train)
            
            self.model = grid_search.best_estimator_
            y_pred = self.model.predict(X_test)
        
        # Métricas del mejor modelo
        metrics = {
            'best_params': grid_search.best_params_,
            'best_score': -grid_search.best_score_,
            'test_mae': mean_absolute_error(y_test, y_pred),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'test_r2': r2_score(y_test, y_pred)
        }
        
        logger.info(f"Optimización completada - Mejores parámetros: {metrics['best_params']}")
        return metrics
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Obtener importancia de características."""
        if self.model is None:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            importance_dict = dict(zip(self.feature_names, self.model.feature_importances_))
            # Ordenar por importancia
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        return {}
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Realizar predicciones."""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        # Aplicar escalado si es XGBoost
        if isinstance(self.model, xgb.XGBRegressor):
            X_scaled = self.scaler.transform(X)
            return self.model.predict(X_scaled)
        else:
            return self.model.predict(X)
    
    def save_model(self, filepath: str):
        """Guardar modelo entrenado."""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metadata': self.model_metadata
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Modelo guardado en: {filepath}")
    
    def load_model(self, filepath: str):
        """Cargar modelo entrenado."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_metadata = model_data['metadata']
        
        logger.info(f"Modelo cargado desde: {filepath}")


def train_and_evaluate_models(df: pd.DataFrame) -> Dict[str, Any]:
    """Entrenar y comparar múltiples modelos."""
    predictor = NeumaticoPredictor()
    
    # Preparar datos
    X, y, feature_names = predictor.prepare_data(df)
    predictor.feature_names = feature_names
    
    results = {}
    
    # Entrenar XGBoost
    logger.info("Entrenando XGBoost...")
    xgb_metrics = predictor.train_xgboost(X, y)
    results['xgboost'] = xgb_metrics
    
    # Guardar modelo XGBoost
    predictor.model_metadata = {
        'model_type': 'xgboost',
        'training_date': datetime.now().isoformat(),
        'n_features': len(feature_names),
        'n_samples': len(X)
    }
    predictor.save_model('ml/modelo_xgboost_v1.pkl')
    
    # Entrenar Random Forest
    logger.info("Entrenando Random Forest...")
    rf_metrics = predictor.train_random_forest(X, y)
    results['random_forest'] = rf_metrics
    
    # Guardar modelo Random Forest
    predictor.model_metadata = {
        'model_type': 'random_forest',
        'training_date': datetime.now().isoformat(),
        'n_features': len(feature_names),
        'n_samples': len(X)
    }
    predictor.save_model('ml/modelo_random_forest_v1.pkl')
    
    # Importancia de características
    feature_importance = predictor.get_feature_importance()
    results['feature_importance'] = feature_importance
    
    return results


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejemplo de uso con datos sintéticos
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = {
        'kilometraje_acumulado': np.random.randint(10000, 200000, n_samples),
        'vida_actual': np.random.randint(1, 5, n_samples),
        'profundidad_remanente_actual_mm': np.random.uniform(2, 16, n_samples),
        'edad_dias': np.random.randint(30, 1800, n_samples),
        'km_por_dia': np.random.uniform(10, 500, n_samples),
        'desgaste_por_km': np.random.uniform(0.001, 0.01, n_samples),
        'vida_util_restante_km': np.random.randint(0, 100000, n_samples)
    }
    
    df = pd.DataFrame(sample_data)
    
    # Entrenar modelos
    results = train_and_evaluate_models(df)
    
    print("Resultados del entrenamiento:")
    print(json.dumps(results, indent=2, default=str))
