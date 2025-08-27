# alembic/env.py

import sys
from os.path import abspath, dirname
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlmodel import SQLModel

# --- Añade la ruta del proyecto para que Alembic encuentre los modelos ---
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# --- Importa TODOS tus modelos de la base de datos aquí ---
from ges_neu_api.auth.models.usuario import Usuario
from ges_neu_api.catalogos.models import Fabricante, ModeloNeumatico
# A medida que creemos más modelos, los añadiremos aquí.

# --------------------------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

# ==============================================================================
# ¡ESTA ES LA PARTE NUEVA Y MÁS IMPORTANTE!
# Le decimos a Alembic que ignore las tablas que no están en nuestro código.
# ==============================================================================
def include_object(object, name, type_, reflected, compare_to):
    """
    Función para que autogenerate solo detecte las tablas definidas en nuestros modelos.
    """
    if type_ == "table" and name not in target_metadata.tables:
        return False
    return True
# ==============================================================================


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Le decimos a Alembic que use nuestra función de filtro
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Le decimos a Alembic que use nuestra función de filtro
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
