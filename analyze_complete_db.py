#!/usr/bin/env python3
"""
Script para analizar completamente la estructura de la base de datos ges_neu_bd
y generar un reporte detallado de todas las 36 tablas.
"""

import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import reflection
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

def analyze_complete_database():
    """Analiza todas las tablas de la base de datos"""
    
    database_url = get_database_url()
    print(f"Conectando a: {database_url.replace(os.getenv('DB_PASSWORD', 'B3ll1c0s'), '***')}")
    
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    # Obtener todas las tablas
    tables = inspector.get_table_names()
    print(f"\n📊 TOTAL DE TABLAS ENCONTRADAS: {len(tables)}\n")
    
    # Agrupar tablas por módulos
    modules = {
        'AUTENTICACIÓN': ['usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos'],
        'VEHÍCULOS': ['vehiculos', 'tipos_vehiculo', 'registros_odometro'],
        'NEUMÁTICOS CORE': ['neumaticos', 'modelos_neumatico', 'fabricantes_neumatico', 'posiciones_neumatico', 'configuraciones_eje'],
        'INVENTARIO': ['inventario_neumaticos', 'movimientos_inventario', 'almacenes', 'parametros_inventario'],
        'BITÁCORAS': ['bitacora_mantenimiento', 'bitacora_operaciones', 'bitacora_operaciones_neumaticos'],
        'AUDITORÍA': ['auditoria_log', 'configuracion_auditoria', 'errores_aplicacion'],
        'MEDICIONES': ['mediciones_profundidad', 'especificaciones_desgaste', 'historial_estados_neumaticos'],
        'GARANTÍAS': ['garantias_neumaticos'],
        'ALERTAS': ['alertas'],
        'EVENTOS': ['eventos_neumaticos'],
        'RUTAS': ['rutas', 'tipos_ruta'],
        'SISTEMA': ['parametros_sistema', 'tareas_programadas'],
        'CONFIGURACIÓN': ['modelos_posiciones_permitidas', 'parametros_rendimiento_esperado_modelo', 'motivos_desecho'],
        'ALEMBIC': ['alembic_version']
    }
    
    # Mostrar tablas por módulo
    for module_name, module_tables in modules.items():
        existing_tables = [t for t in module_tables if t in tables]
        if existing_tables:
            print(f"🔹 **{module_name}** ({len(existing_tables)} tablas):")
            for table in existing_tables:
                # Contar registros
                try:
                    with engine.connect() as conn:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.fetchone()[0]
                        print(f"   - {table} ({count} registros)")
                except Exception as e:
                    print(f"   - {table} (error: {e})")
            print()
    
    # Tablas no categorizadas
    categorized = []
    for module_tables in modules.values():
        categorized.extend(module_tables)
    
    uncategorized = [t for t in tables if t not in categorized]
    if uncategorized:
        print(f"🔸 **OTRAS TABLAS** ({len(uncategorized)} tablas):")
        for table in uncategorized:
            print(f"   - {table}")
        print()
    
    # Resumen de complejidad
    print("=" * 60)
    print("📈 **ANÁLISIS DE COMPLEJIDAD**")
    print("=" * 60)
    
    total_records = 0
    complex_tables = []
    
    for table in tables:
        try:
            with engine.connect() as conn:
                # Contar registros
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                total_records += count
                
                # Contar columnas
                columns = inspector.get_columns(table)
                col_count = len(columns)
                
                if col_count > 10 or count > 50:
                    complex_tables.append((table, count, col_count))
                    
        except Exception:
            pass
    
    print(f"📊 Total de registros en BD: {total_records}")
    print(f"🏗️  Total de tablas: {len(tables)}")
    
    if complex_tables:
        print(f"\n🔥 **TABLAS COMPLEJAS** (>10 columnas o >50 registros):")
        for table, records, cols in sorted(complex_tables, key=lambda x: x[1], reverse=True):
            print(f"   - {table}: {records} registros, {cols} columnas")
    
    return len(tables)

if __name__ == "__main__":
    try:
        total_tables = analyze_complete_database()
        print(f"\n✅ Análisis completado: {total_tables} tablas procesadas")
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        sys.exit(1)
