# gesneu_api2/core/config.py
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Variables de Configuración Originales (¡Importante mantenerlas!) ---
    PROJECT_NAME: str = "GesNeuAPI"
    API_V1_STR: str = "/api/v1" # <--- ATRIBUTO AÑADIDO AQUÍ
    LOG_LEVEL: str = "INFO" # Niveles comunes: DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Seguridad
    SECRET_KEY: str = "B3ll1c0s"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 días, considera un valor menor para producción

    # Database URLs
    # Esta variable DEBE estar definida en tu archivo .env o como variable de entorno
    DATABASE_URL: str
    # URLs para bases de datos de prueba, opcionales si no se usan o se definen en .env
    DATABASE_TEST_URL_HOST: Optional[str] = "sqlite+aiosqlite:///./test_db_host.db"
    DATABASE_TEST_URL_DOCKER: Optional[str] = "postgresql+asyncpg://test_user:test_password@db_test:5432/test_db"

    # Primer superusuario (opcional, para creación inicial)
    FIRST_SUPERUSER_USERNAME: Optional[str] = "admin"
    FIRST_SUPERUSER_EMAIL: Optional[str] = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: Optional[str] = "adminpassword"

    # CORS Origins
    # Especificar los orígenes permitidos. "*" es inseguro para producción.
    # Ejemplo: "http://localhost:3000,http://mi.dominio.app"
    BACKEND_CORS_ORIGINS: str = "*" # Cambiar en producción

    # Umbral para alertas (ejemplo)
    UMBRAL_PROFUNDIDAD_MINIMA_MM: float = 1.6
    
    # Configuración para pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",          # Carga variables desde el archivo .env
        env_file_encoding='utf-8', # Codificación del archivo .env
        case_sensitive=True,      # Distingue mayúsculas/minúsculas en nombres de variables de entorno
        extra='ignore'            # Ignora variables extra en .env que no estén definidas en esta clase
    )

# Instancia cacheada de la configuración
@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de la configuración.
    Esto asegura que el archivo .env y las variables de entorno se lean solo una vez.
    """
    print("DEBUG: Cargando configuración...") # Mensaje para depuración
    try:
        settings_instance = Settings()
        # Verificar que DATABASE_URL se cargó correctamente
        if not settings_instance.DATABASE_URL:
             # Esta verificación es un poco redundante si DATABASE_URL no tiene default y no es Optional,
             # ya que Pydantic fallaría antes si no se proporciona. Pero no hace daño.
             raise ValueError("DATABASE_URL no está definida en .env ni como variable de entorno.")
        print(f"DEBUG: Configuración cargada. DATABASE_URL={settings_instance.DATABASE_URL[:25]}...") # Mostrar inicio de la URL
        return settings_instance
    except ValueError as e:
         print(f"ERROR FATAL AL CARGAR CONFIGURACIÓN: {e}")
         # Considera terminar la aplicación si la configuración es esencial y falla.
         # import sys
         # sys.exit(f"Error crítico de configuración: {e}")
         raise # Re-lanzar la excepción para que el fallo sea evidente al iniciar la app

# Crear la instancia global de settings que se importará en otros módulos
settings = get_settings()
