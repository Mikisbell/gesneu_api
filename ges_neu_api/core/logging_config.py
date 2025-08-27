"""
Configuración centralizada de logging para la API.

Este módulo configura el sistema de logging de Python para proporcionar
registros estructurados y consistentes en toda la aplicación.
"""
import logging
import logging.config
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseSettings, Field

# Directorio base para los logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Niveles de log disponibles
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LoggingSettings(BaseSettings):
    """Configuración del sistema de logging."""
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato de los mensajes de log"
    )
    
    LOG_FILE: str = Field(
        default=str(LOG_DIR / "app.log"),
        description="Ruta del archivo de log principal"
    )
    
    LOG_MAX_BYTES: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Tamaño máximo del archivo de log antes de rotar"
    )
    
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        description="Número de archivos de respaldo a mantener"
    )
    
    # Validación del nivel de log
    class Config:
        @classmethod
        def validate_log_level(cls, v: str) -> str:
            if v.upper() not in LOG_LEVELS:
                raise ValueError(f"LOG_LEVEL debe ser uno de: {', '.join(LOG_LEVELS)}")
            return v.upper()
        
        @classmethod
        def customise_sources(cls, init_settings):
            return (
                init_settings.init_settings,
                cls.validate_log_level,
            )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    ""
    Obtiene un logger con la configuración establecida.
    
    Args:
        name: Nombre del logger. Si es None, devuelve el logger raíz.
    """
    return logging.getLogger(name or __name__)


def setup_logging() -> None:
    """Configura el sistema de logging de la aplicación."""
    try:
        settings = LoggingSettings()
        
        # Configuración básica
        logging.basicConfig(
            level=settings.LOG_LEVEL,
            format=settings.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.handlers.RotatingFileHandler(
                    settings.LOG_FILE,
                    maxBytes=settings.LOG_MAX_BYTES,
                    backupCount=settings.LOG_BACKUP_COUNT,
                    encoding="utf-8"
                )
            ]
        )
        
        # Configurar el nivel de log para bibliotecas de terceros
        logging.getLogger("sqlalchemy.engine").setLevel("WARNING")
        logging.getLogger("uvicorn.access").handlers = logging.getLogger().handlers
        
        logger = get_logger(__name__)
        logger.info("Sistema de logging configurado correctamente")
        
    except Exception as e:
        # Si falla la configuración, usar configuración básica
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Error al configurar el logging: {e}")


# Configuración de logging estructurado para JSON
class StructuredLogFormatter(logging.Formatter):
    """Formateador de logs en formato JSON estructurado."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        
        # Agregar atributos personalizados
        if hasattr(record, 'props') and isinstance(record.props, dict):  # type: ignore
            log_record.update(record.props)  # type: ignore
        
        return self._to_json(log_record)
    
    def _to_json(self, data: Dict[str, Any]) -> str:
        """Convierte un diccionario a JSON de forma segura."""
        import json
        return json.dumps(data, ensure_ascii=False, default=str)


def setup_structured_logging() -> None:
    """Configura el logging estructurado en formato JSON."""
    try:
        settings = LoggingSettings()
        
        # Crear el formateador
        formatter = StructuredLogFormatter()
        
        # Configurar el handler de consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Configurar el handler de archivo
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE.replace('.log', '_structured.log'),
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        
        # Configurar el logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(settings.LOG_LEVEL)
        
        # Eliminar handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Agregar los nuevos handlers
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # Configurar niveles para bibliotecas de terceros
        logging.getLogger("sqlalchemy.engine").setLevel("WARNING")
        logging.getLogger("uvicorn.access").handlers = []
        
        logger = get_logger(__name__)
        logger.info("Sistema de logging estructurado configurado correctamente")
        
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Error al configurar el logging estructurado: {e}")


# Configurar logging al importar el módulo
setup_logging()
