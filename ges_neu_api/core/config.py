"""
Configuración centralizada de la aplicación.

Este módulo utiliza Pydantic Settings para manejar la configuración
de la aplicación a través de variables de entorno.
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuración básica de la aplicación
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Configuración de la aplicación
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    APP_SECRET_KEY: str
    APP_DOMAIN: str = "localhost"
    
    # Configuración de la base de datos
    DB_DRIVER: str = "postgresql+asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "ges_neu_bd"
    DB_USER: str = "postgres"
    DB_PASSWORD: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    
    # Configuración de base de datos de test
    TEST_DB_DRIVER: str = "sqlite+aiosqlite"
    TEST_DB_NAME: str = ":memory:"
    
    # Configuración de autenticación
    JWT_SECRET_KEY: str = "test-secret-key-for-development-only"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def TEST_SQLALCHEMY_DATABASE_URI(self) -> str:
        """URI de base de datos para tests (SQLite en memoria)."""
        return f"{self.TEST_DB_DRIVER}:///{self.TEST_DB_NAME}"
    
    # Configuración del servidor
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000
    WORKERS: int = 1
    
    # Configuración de la API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GES_NEU API"
    PROJECT_DESCRIPTION: str = "API para el sistema de Gestión de Neumáticos"
    PROJECT_VERSION: str = "0.1.0"


@lru_cache()
def get_settings() -> Settings:
    """
    Devuelve una instancia de configuración.
    
    Esta función está decorada con @lru_cache para evitar recrear
    la configuración en cada llamada, mejorando el rendimiento.
    """
    return Settings()


# Instancia de configuración global
settings = get_settings()
