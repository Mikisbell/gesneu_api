"""
Script para verificar la definición de los modelos sin ejecutar tests.
"""
import asyncio
import sys
from pathlib import Path

# Asegurarse de que el directorio raíz del proyecto está en el path
project_root = str(Path(__file__).parent.resolve())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel

# Importar todos los modelos para que SQLAlchemy los registre
from ges_neu_api.modules.auth.models import *
from ges_neu_api.modules.vehiculos.models import *
from ges_neu_api.modules.neumaticos.models import *
from ges_neu_api.modules.inventario.models import *
from ges_neu_api.modules.eventos.models import *
from ges_neu_api.modules.garantias.models import *
from ges_neu_api.modules.alertas.models import *

async def check_models():
    """Verifica que los modelos estén correctamente definidos."""
    # Usar SQLite en memoria para la verificación
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Obtener información de las tablas
    async with AsyncSession(engine) as session:
        inspector = inspect(await session.connection())
        table_names = inspector.get_table_names()
        
        print("\n=== TABLAS ENCONTRADAS ===")
        for table_name in sorted(table_names):
            print(f"- {table_name}")
            
            # Obtener columnas
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  - {column['name']}: {column['type']}", 
                      f"(PK: {'✅' if column.get('primary_key') else ' '})",
                      f"(NULL: {'✅' if column.get('nullable') else '❌'})")
            
            # Obtener claves foráneas
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print("  \n  === CLAVES FORÁNEAS ===")
                for fk in fks:
                    print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    print("Iniciando verificación de modelos...")
    asyncio.run(check_models())
    print("Verificación completada. Revise la salida para ver los detalles de los modelos.")
