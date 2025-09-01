#!/usr/bin/env python3
"""
Script para comparar los modelos SQLModel actuales con el esquema real 
extraído de backup_completo.dump (archivo generated_models.py)
"""

import re
from pathlib import Path

def extract_table_info_from_generated():
    """Extrae información de tablas del archivo generated_models.py"""
    
    with open('generated_models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las clases que representan tablas
    table_pattern = r'class\s+(\w+)\(Base\):\s*\n\s*__tablename__\s*=\s*[\'"]([^\'"]+)[\'"]'
    tables = re.findall(table_pattern, content)
    
    print("=== TABLAS REALES EN LA BASE DE DATOS ===")
    print(f"(Extraídas de backup_completo.dump via generated_models.py)")
    print()
    
    real_tables = {}
    for class_name, table_name in tables:
        real_tables[table_name] = class_name
        print(f"✅ {table_name} -> {class_name}")
    
    print(f"\nTotal: {len(real_tables)} tablas reales")
    return real_tables

def check_current_models():
    """Verifica los modelos SQLModel actuales"""
    
    model_files = {
        'auth': 'ges_neu_api/modules/auth/models.py',
        'vehiculos': 'ges_neu_api/modules/vehiculos/models.py',
        'catalogos': 'ges_neu_api/modules/catalogos/models.py', 
        'neumaticos': 'ges_neu_api/modules/neumaticos/models.py',
        'bitacoras': 'ges_neu_api/modules/bitacoras/models.py',
        'sistema': 'ges_neu_api/modules/sistema/models.py'
    }
    
    print("\n=== MODELOS SQLMODEL ACTUALES ===")
    
    current_models = {}
    for module, file_path in model_files.items():
        if Path(file_path).exists():
            print(f"\n{module.upper()} MODULE:")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar clases con table=True
                table_pattern = r'class\s+(\w+)\([^)]*table=True[^)]*\):\s*\n\s*__tablename__\s*=\s*[\'"]([^\'"]+)[\'"]'
                tables = re.findall(table_pattern, content)
                
                for class_name, table_name in tables:
                    current_models[table_name] = (class_name, module)
                    print(f"  ✅ {table_name} -> {class_name}")
                    
            except Exception as e:
                print(f"  ❌ Error leyendo {file_path}: {e}")
        else:
            print(f"  ❌ Archivo faltante: {file_path}")
    
    return current_models

def compare_schemas():
    """Compara esquemas real vs actual"""
    
    print("\n" + "="*60)
    print("COMPARACIÓN ESQUEMA REAL vs MODELOS ACTUALES")
    print("="*60)
    
    real_tables = extract_table_info_from_generated()
    current_models = check_current_models()
    
    print(f"\n📊 RESUMEN:")
    print(f"  - Tablas reales en BD: {len(real_tables)}")
    print(f"  - Modelos SQLModel actuales: {len(current_models)}")
    
    # Tablas que existen en BD pero no en modelos
    missing_in_models = set(real_tables.keys()) - set(current_models.keys())
    if missing_in_models:
        print(f"\n❌ TABLAS FALTANTES EN MODELOS ({len(missing_in_models)}):")
        for table in sorted(missing_in_models):
            print(f"  - {table}")
    
    # Tablas que existen en modelos pero no en BD
    extra_in_models = set(current_models.keys()) - set(real_tables.keys())
    if extra_in_models:
        print(f"\n⚠️  MODELOS EXTRA (no en BD) ({len(extra_in_models)}):")
        for table in sorted(extra_in_models):
            module = current_models[table][1]
            print(f"  - {table} (módulo: {module})")
    
    # Tablas que coinciden
    matching_tables = set(real_tables.keys()) & set(current_models.keys())
    if matching_tables:
        print(f"\n✅ TABLAS COINCIDENTES ({len(matching_tables)}):")
        for table in sorted(matching_tables):
            module = current_models[table][1]
            print(f"  - {table} (módulo: {module})")
    
    return real_tables, current_models, missing_in_models, extra_in_models

if __name__ == "__main__":
    try:
        compare_schemas()
        print(f"\n✅ Comparación completada")
    except Exception as e:
        print(f"❌ Error: {e}")
