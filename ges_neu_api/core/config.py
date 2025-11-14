"""
Configuración centralizada de la aplicación.

Este módulo utiliza Pydantic Settings para manejar la configuración
de la aplicación a través de variables de entorno.
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuración básica de la aplicación
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # =========================
    # Configuración de la aplicación
    # =========================
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_secret_key: str = Field(..., alias="APP_SECRET_KEY")
    app_domain: str = Field(default="localhost", alias="APP_DOMAIN")
    
    # =========================
    # Configuración de la base de datos
    # =========================
    db_driver: str = Field(default="postgresql+asyncpg", alias="DB_DRIVER")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="ges_neu_bd", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=30, alias="DB_MAX_OVERFLOW")
    
    # =========================
    # Configuración de base de datos de test
    # =========================
    test_db_driver: str = Field(default="sqlite+aiosqlite", alias="TEST_DB_DRIVER")
    test_db_name: str = Field(default=":memory:", alias="TEST_DB_NAME")
    
    # =========================
    # Configuración de autenticación
    # =========================
    jwt_secret_key: str = Field(default="test-secret-key-for-development-only", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # =========================
    # Configuración de CORS
    # =========================
    backend_cors_origins: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"], alias="BACKEND_CORS_ORIGINS")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # =========================
    # Configuración de la API
    # =========================
    api_v1_str: str = Field(default="/api/v1", alias="API_V1_STR")
    project_name: str = Field(default="GES_NEU API", alias="PROJECT_NAME")
    project_description: str = Field(default="API para el sistema de Gestión de Neumáticos", alias="PROJECT_DESCRIPTION")
    project_version: str = Field(default="0.1.0", alias="PROJECT_VERSION")
    
    # =========================
    # Configuración del servidor
    # =========================
    server_host: str = Field(default="127.0.0.1", alias="SERVER_HOST")
    server_port: int = Field(default=8000, alias="SERVER_PORT")
    workers: int = Field(default=1, alias="WORKERS")

    # =========================
    # Propiedades útiles
    # =========================
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def TEST_SQLALCHEMY_DATABASE_URI(self) -> str:
        """URI de base de datos para tests (SQLite en memoria)."""
        return f"{self.test_db_driver}:///{self.test_db_name}"


@lru_cache()
def get_settings() -> Settings:
    """
    Devuelve una instancia de configuración.
    
    Esta función está decorada con @lru_cache para evitar recrear
    la configuración en cada llamada, mejorando el rendimiento.
    """
    # BaseSettings resuelve campos requeridos desde variables de entorno en tiempo de ejecución.
    # mypy no puede inferir esos valores y marca falta de argumentos nombrados.
    return Settings()  # type: ignore[call-arg]


# Instancia de configuración global
settings = get_settings()
