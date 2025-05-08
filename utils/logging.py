# gesneu_api2/utils/logging.py
import logging
import sys # Para StreamHandler a stdout
from pathlib import Path
from core.config import settings # Para obtener el nivel de log desde la configuración

# Nombre para el logger de la aplicación
APP_LOGGER_NAME = settings.PROJECT_NAME # O un nombre específico como "gesneu_api_logger"

def setup_logging(log_level_str: str = settings.LOG_LEVEL):
    """
    Configura el logging básico para la aplicación.
    Utiliza el nivel de log especificado en la configuración.
    """
    # Convertir el string del nivel de log a un valor numérico de logging
    numeric_log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Crear el directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "app.log"

    # Configuración básica
    # Se remueven los handlers por defecto para evitar duplicados si se llama múltiples veces
    # o si otros módulos también configuran basicConfig.
    # Es mejor configurar handlers directamente en el logger específico.
    # logging.basicConfig(level=numeric_log_level, format=log_format) # Evitar basicConfig si se configuran loggers específicos

    # Obtener el logger específico de la aplicación
    logger_instance = logging.getLogger(APP_LOGGER_NAME)
    logger_instance.setLevel(numeric_log_level) # Establecer el nivel para este logger

    # Evitar añadir handlers múltiples veces si esta función se llama más de una vez
    if not logger_instance.handlers:
        # Formato del log
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
        formatter = logging.Formatter(log_format)

        # Handler para escribir a un archivo
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger_instance.addHandler(file_handler)

        # Handler para escribir a la consola (stdout)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger_instance.addHandler(stream_handler)
    
    return logger_instance

# Crear y configurar la instancia del logger que será importada por otros módulos
# Esta función setup_logging() se llamará una vez cuando este módulo se importe por primera vez.
logger = setup_logging()

# Opcionalmente, podrías querer configurar el logger raíz también,
# pero para aplicaciones es mejor usar loggers nombrados.
# Por ejemplo, para silenciar otros loggers (como uvicorn access) o cambiar su nivel:
# logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO) # Para ver queries SQL
