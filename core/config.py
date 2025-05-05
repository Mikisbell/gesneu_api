# core/config.py (Versión Completa y Corregida)

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
# Quitar 'os' si ya no se usa directamente aquí
# import os
from functools import lru_cache

class Settings(BaseSettings):
    # --- Variables de Configuración Originales (¡Importante mantenerlas!) ---
    PROJECT_NAME: str = "GesNeu API" # <-- Necesario para main.py
    API_V1_STR: str = "/api/v1"

    # Seguridad (Leer desde .env o usar defaults si no están)
    SECRET_KEY: str = "una_clave_secreta_por_defecto_insegura" # Default por si no está en .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 días

    # Database URLs (Leer desde .env o usar defaults)
    # Asegúrate que DATABASE_URL esté en tu .env
    DATABASE_URL: str # <- Hacerla obligatoria aquí para que falle si no está en .env
    DATABASE_TEST_URL_HOST: Optional[str] = "sqlite+aiosqlite:///./test_db_host.db" # Para pruebas locales con otra BD
    # URL para la BD de prueba en Docker (puede venir de .env si es necesario)
    DATABASE_TEST_URL_DOCKER: Optional[str] = "postgresql+asyncpg://test_user:test_password@db_test:5432/test_db"

    # Primer usuario (opcional, considerar método seguro)
    FIRST_SUPERUSER_USERNAME: Optional[str] = "admin"
    FIRST_SUPERUSER_EMAIL: Optional[str] = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: Optional[str] = "adminpassword"

    # CORS Origins (Leer desde .env o usar default)
    # CUIDADO: "*" permite cualquier origen, sé más específico en producción
    BACKEND_CORS_ORIGINS: str = "*"

    # Umbral para alertas (Leer desde .env o usar default)
    UMBRAL_PROFUNDIDAD_MINIMA_MM: float = 1.6
    # ---------------------------------------------------------------------

    # --- Nueva Configuración con model_config (Correcto) ---
    model_config = SettingsConfigDict(
        env_file=".env",          # Carga .env si existe
        env_file_encoding='utf-8',
        case_sensitive=True,      # Distingue mayúsculas/minúsculas en variables de entorno
        extra='ignore'            # Ignora variables extra en .env que no estén definidas aquí
    )

# --- Instancia Cacheada (Correcto) ---
@lru_cache()
def get_settings() -> Settings:
    print("DEBUG: Cargando configuración...") # Añadir log/print si quieres ver cuándo carga
    try:
        settings_instance = Settings()
        # Verificar que DATABASE_URL se cargó (era obligatoria)
        if not settings_instance.DATABASE_URL:
             raise ValueError("DATABASE_URL no está definida en .env ni como variable de entorno.")
        print(f"DEBUG: Configuración cargada. DATABASE_URL={settings_instance.DATABASE_URL[:15]}...") # Mostrar inicio URL
        return settings_instance
    except ValueError as e:
         print(f"ERROR FATAL AL CARGAR CONFIGURACIÓN: {e}")
         # Podrías salir de la aplicación aquí si la config es esencial
         # import sys
         # sys.exit(1)
         raise e # O re-lanzar para que falle el inicio


settings = get_settings()