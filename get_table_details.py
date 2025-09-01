#!/usr/bin/env python3
"""
Script para obtener detalles completos de todas las tablas faltantes
"""

import os
from sqlalchemy import create_engine, text, inspect
import sys

# Configurar encoding para Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def get_database_url():
    """Construye la URL de conexión desde variables de entorno"""
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'B3ll1c0s')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ges_neu_bd')
    
    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def get_table_details(table_name):
    """Obtiene detalles completos de una tabla"""
    engine = create_engine(get_database_url())
    inspector = inspect(engine)
    
    print(f"\n=== {table_name.upper()} ===")
    
    # Columnas
    columns = inspector.get_columns(table_name)
    print("Columnas:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        col_type = str(col['type'])
        print(f"  - {col['name']}: {col_type} {nullable}")
    
    # Claves primarias
    pk = inspector.get_pk_constraint(table_name)
    if pk['constrained_columns']:
        print(f"PK: {', '.join(pk['constrained_columns'])}")
    
    # Claves foráneas
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print("FK:")
        for fk in fks:
            local_cols = ', '.join(fk['constrained_columns'])
            ref_table = fk['referred_table']
            ref_cols = ', '.join(fk['referred_columns'])
            print(f"  {local_cols} -> {ref_table}.{ref_cols}")

if __name__ == "__main__":
    # Tablas faltantes críticas
    missing_tables = [
        'fabricantes_neumatico',
        'bitacora_mantenimiento', 
        'bitacora_operaciones',
        'bitacora_operaciones_neumaticos',
        'auditoria_log',
        'configuracion_auditoria',
        'errores_aplicacion',
        'eventos_neumaticos',
        'mediciones_profundidad',
        'especificaciones_desgaste',
        'historial_estados_neumaticos',
        'garantias_neumaticos',
        'alertas',
        'modelos_posiciones_permitidas',
        'parametros_rendimiento_esperado_modelo',
        'motivos_desecho'
    ]
    
    for table in missing_tables:
        try:
            get_table_details(table)
        except Exception as e:
            print(f"Error con tabla {table}: {e}")
