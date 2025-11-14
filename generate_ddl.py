"""
Genera el DDL (CREATE TABLE ...) para TODOS los modelos usando el dialecto PostgreSQL
SIN conectarse a ninguna base de datos.

Uso:
  python generate_ddl.py > ddl.sql
"""
from pathlib import Path
import sys

# Añadir raíz del proyecto al path
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from sqlmodel import SQLModel

# Importar todos los modelos para registrar sus tablas en SQLModel.metadata
from ges_neu_api.modules.auth.models import *  # noqa
from ges_neu_api.modules.vehiculos.models import *  # noqa
from ges_neu_api.modules.neumaticos.models import *  # noqa
from ges_neu_api.modules.inventario.models import *  # noqa
from ges_neu_api.modules.eventos.models import *  # noqa
from ges_neu_api.modules.garantias.models import *  # noqa
from ges_neu_api.modules.alertas.models import *  # noqa
from ges_neu_api.modules.catalogos.models import *  # noqa
from ges_neu_api.modules.bitacoras.models import *  # noqa


def main() -> None:
    dialect = postgresql.dialect()
    print("-- DDL generado para PostgreSQL")
    print("-- Archivo: ddl.sql\n")

    for table_name, table in sorted(SQLModel.metadata.tables.items()):
        try:
            ddl = str(CreateTable(table).compile(dialect=dialect))
            print(f"-- Tabla: {table_name}")
            print(ddl + ";\n")
        except Exception as e:
            print(f"-- [ERROR] No se pudo generar DDL para {table_name}: {e}\n")


if __name__ == "__main__":
    main()
