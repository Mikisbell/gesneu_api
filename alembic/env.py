from logging.config import fileConfig
import sys
from os.path import abspath, dirname
from typing import List, Union, Dict, Any

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Agregar el directorio raíz del proyecto al path de Python
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# Importar la configuración de la aplicación para obtener la URL de la base de datos
from ges_neu_api.core.config import settings

# Importar todos los modelos para que SQLModel los registre
# Asegúrate de importar todos los modelos de tu aplicación
from ges_neu_api.auth.models.usuario import Usuario
from ges_neu_api.catalogos.models.fabricante import Fabricante
from ges_neu_api.catalogos.models.modelo_neumatico import ModeloNeumatico
# Agrega aquí otros modelos según sea necesario

# Configuración de Alembic
config = context.config

# Interpretar el archivo de configuración para el logging de Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Agregar la URL de la base de datos de la configuración de la aplicación
config.set_main_option('sqlalchemy.url', settings.SQLALCHEMY_DATABASE_URI)

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'.
    
    Esto configura el contexto con solo una conexión URL y no un Engine,
    aunque también se acepta un Engine, omitiendo la necesidad de una URL.
    Las llamadas a context.execute() emiten el texto dado a la salida del script.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'.
    
    En este escenario necesitamos crear un Engine
    y asociar una conexión con el contexto.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

def include_object(
    object: Any, name: str, type_: str, reflected: bool, compare_to: Any
) -> bool:
    """Filtra qué objetos incluir en las migraciones.
    
    Args:
        object: El objeto de esquema que se está considerando.
        name: Nombre del objeto.
        type_: Tipo de objeto (table, index, etc.).
        reflected: Si el objeto fue producido por reflexión.
        compare_to: El objeto que se está comparando, si existe.
    
    Returns:
        bool: True si el objeto debe incluirse en la migración.
    """
    # Ignorar tablas que no están en nuestros modelos
    if type_ == "table" and name not in target_metadata.tables:
        return False
        
    # Ignorar índices automáticos de SQLModel
    if type_ == "index" and name.startswith("ix_"):
        return False
        
    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
