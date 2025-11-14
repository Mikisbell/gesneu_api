#!/usr/bin/env python3
"""
Verificación completa de alineación entre modelos SQLModel y esquema PostgreSQL real
Basado en ESQUEMA_COMPLETO_BD.md
"""

import os
import sys
from pathlib import Path
import importlib.util
from typing import Dict, List, Any
import re

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def load_schema_from_md() -> Dict[str, Any]:
    """Cargar esquema real desde ESQUEMA_COMPLETO_BD.md"""
    schema_file = Path("ESQUEMA_COMPLETO_BD.md")
    if not schema_file.exists():
        print("❌ ESQUEMA_COMPLETO_BD.md no encontrado")
        return {}
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer tablas del esquema
    tables = {}
    
    # Buscar todas las secciones de tablas
    table_pattern = r'### ([a-z_]+)\s*\n\n#### Columnas\s*\n\n\| Columna \| Tipo \| Nulable \| Por Defecto \| Descripción \|\s*\n\|[^|]+\|\s*\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^|]*\|\s*\n)*)'
    
    matches = re.finditer(table_pattern, content, re.MULTILINE)
    
    for match in matches:
        table_name = match.group(1)
        columns_text = match.group(2)
        
        columns = {}
        for line in columns_text.strip().split('\n'):
            if line.strip() and '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    col_name = parts[0]
                    col_type = parts[1]
                    nullable = parts[2].lower() == 'sí'
                    default = parts[3] if parts[3] != '' else None
                    columns[col_name] = {
                        'type': col_type,
                        'nullable': nullable,
                        'default': default
                    }
        
        tables[table_name] = {'columns': columns}
    
    # Extraer enums
    enums = {}
    enum_pattern = r'### ([a-z_]+_enum)\s*\n```sql\s*\nCREATE TYPE [^(]+\(\s*\n((?:\s*\'[^\']+\',?\s*\n)*)\s*\);'
    
    enum_matches = re.finditer(enum_pattern, content, re.MULTILINE)
    
    for match in enum_matches:
        enum_name = match.group(1)
        values_text = match.group(2)
        
        values = []
        for line in values_text.strip().split('\n'):
            if line.strip():
                value = line.strip().strip("',")
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                values.append(value)
        
        enums[enum_name] = values
    
    return {'tables': tables, 'enums': enums}

def get_all_models() -> Dict[str, Any]:
    """Obtener todos los modelos SQLModel del proyecto"""
    models = {}
    
    modules_dir = Path("ges_neu_api/modules")
    if not modules_dir.exists():
        print("❌ Directorio de módulos no encontrado")
        return {}
    
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir() and (module_dir / "models.py").exists():
            module_name = module_dir.name
            models_file = module_dir / "models.py"
            
            try:
                # Cargar el módulo dinámicamente
                spec = importlib.util.spec_from_file_location(f"{module_name}_models", models_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Buscar clases SQLModel
                module_models = {}
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (hasattr(attr, '__tablename__') and 
                        hasattr(attr, '__table__') and 
                        attr_name not in ['SQLModel']):
                        
                        table_name = getattr(attr, '__tablename__', None)
                        if table_name:
                            module_models[table_name] = {
                                'class_name': attr_name,
                                'class_obj': attr
                            }
                
                models[module_name] = module_models
                
            except Exception as e:
                print(f"⚠️  Error cargando modelos de {module_name}: {e}")
    
    return models

def verify_alignment():
    """Verificar alineación completa"""
    print("🔍 VERIFICACIÓN COMPLETA DE ALINEACIÓN")
    print("=" * 50)
    
    # Cargar esquema real
    schema = load_schema_from_md()
    if not schema:
        return
    
    real_tables = schema.get('tables', {})
    real_enums = schema.get('enums', {})
    
    print(f"📊 Esquema real: {len(real_tables)} tablas, {len(real_enums)} enums")
    
    # Cargar modelos del código
    code_models = get_all_models()
    
    total_code_tables = sum(len(models) for models in code_models.values())
    print(f"💻 Código: {total_code_tables} modelos en {len(code_models)} módulos")
    
    print("\n" + "=" * 50)
    
    # Verificar tablas faltantes en código
    missing_in_code = []
    for table_name in real_tables:
        found = False
        for module_models in code_models.values():
            if table_name in module_models:
                found = True
                break
        if not found:
            missing_in_code.append(table_name)
    
    # Verificar tablas extra en código
    extra_in_code = []
    for module_name, module_models in code_models.items():
        for table_name in module_models:
            if table_name not in real_tables:
                extra_in_code.append(f"{module_name}.{table_name}")
    
    # Resultados
    print("📋 RESULTADOS DE VERIFICACIÓN:")
    print("-" * 30)
    
    if missing_in_code:
        print(f"❌ TABLAS FALTANTES EN CÓDIGO ({len(missing_in_code)}):")
        for table in missing_in_code:
            print(f"   - {table}")
    else:
        print("✅ Todas las tablas del esquema están implementadas")
    
    if extra_in_code:
        print(f"\n⚠️  TABLAS EXTRA EN CÓDIGO ({len(extra_in_code)}):")
        for table in extra_in_code:
            print(f"   - {table}")
    else:
        print("\n✅ No hay tablas extra en el código")
    
    # Verificar enums
    print(f"\n🔢 VERIFICACIÓN DE ENUMS:")
    print(f"   Esquema real: {len(real_enums)} enums")
    print("   Principales enums encontrados:")
    for enum_name, values in list(real_enums.items())[:5]:
        print(f"   - {enum_name}: {len(values)} valores")
    
    # Resumen final
    alignment_score = ((len(real_tables) - len(missing_in_code)) / len(real_tables)) * 100 if real_tables else 100
    
    print(f"\n📊 PUNTUACIÓN DE ALINEACIÓN: {alignment_score:.1f}%")
    
    if alignment_score == 100 and not extra_in_code:
        print("🎉 ¡ALINEACIÓN PERFECTA!")
    elif alignment_score >= 90:
        print("✅ Alineación excelente")
    elif alignment_score >= 75:
        print("⚠️  Alineación buena, necesita mejoras")
    else:
        print("❌ Alineación deficiente, requiere corrección")
    
    return {
        'alignment_score': alignment_score,
        'missing_tables': missing_in_code,
        'extra_tables': extra_in_code,
        'total_real_tables': len(real_tables),
        'total_code_tables': total_code_tables
    }

if __name__ == "__main__":
    verify_alignment()
