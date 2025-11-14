"""
Genera el DDL (CREATE TABLE ...) SOLO para el módulo AUTH usando el dialecto PostgreSQL
SIN conectarse a ninguna base de datos.

Evita importar paquetes que disparan cargas de settings (p. ej., core.config)
cargando directamente el archivo ges_neu_api/modules/auth/models.py por ruta.

Uso:
  python generate_ddl_auth.py > ddl_auth.sql
"""
from pathlib import Path
import sys
import importlib.util

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from sqlmodel import SQLModel


def load_module_from_path(module_name: str, file_path: Path):
    """Carga un módulo de Python desde un archivo sin ejecutar __init__ de paquetes."""
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo crear spec para {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    project_root = Path(__file__).parent.resolve()
    auth_models_path = project_root / "ges_neu_api" / "modules" / "auth" / "models.py"

    # Cargar el módulo de modelos de AUTH sin ejecutar paquetes intermedios
    load_module_from_path("auth_models_dynamic", auth_models_path)

    # Compilar DDL para solo las tablas definidas hasta ahora (AUTH)
    dialect = postgresql.dialect()
    print("-- DDL generado para PostgreSQL (AUTH)")
    print("-- Archivo: ddl_auth.sql\n")

    # Filtrar tablas de AUTH por nombre conocido
    auth_table_names = {"usuarios", "roles", "permisos", "usuarios_roles", "roles_permisos"}

    for table_name, table in sorted(SQLModel.metadata.tables.items()):
        if table_name not in auth_table_names:
            continue
        try:
            ddl = str(CreateTable(table).compile(dialect=dialect))
            print(f"-- Tabla: {table_name}")
            print(ddl + ";\n")
        except Exception as e:
            print(f"-- [ERROR] No se pudo generar DDL para {table_name}: {e}\n")


if __name__ == "__main__":
    main()
