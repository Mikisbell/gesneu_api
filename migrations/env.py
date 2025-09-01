from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all your models to ensure metadata is complete
from ges_neu_api.core.base_models import BaseModel

# Import all models for Alembic to detect
from ges_neu_api.modules.auth.models import Usuario, Rol, Permiso, UsuariosRoles, RolesPermisos
from ges_neu_api.modules.vehiculos.models import Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico, RegistrosOdometro
from ges_neu_api.modules.catalogos.models import Proveedor, MotivoDesecho, Almacen, ParametroInventario
from ges_neu_api.modules.neumaticos.models import Neumatico, ModeloNeumatico, FabricanteNeumatico
from ges_neu_api.modules.inventario.models import InventarioNeumaticos, MovimientosInventario
from ges_neu_api.modules.eventos.models import EventosNeumaticos, HistorialEstadosNeumaticos, MedicionesProfundidad
from ges_neu_api.modules.garantias.models import GarantiasNeumaticos
from ges_neu_api.modules.alertas.models import Alertas
from ges_neu_api.modules.bitacoras.models import BitacoraMantenimiento, BitacoraOperaciones, AuditoriaLog, ConfiguracionAuditoria, ErroresAplicacion, AuditoriaRolesUsuarios, ParametrosSistema, TareasProgramadas, Rutas, TiposRuta

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = BaseModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
