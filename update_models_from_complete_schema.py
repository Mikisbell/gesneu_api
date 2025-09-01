#!/usr/bin/env python3
"""
Script para actualizar modelos SQLModel basado en ESQUEMA_COMPLETO_BD.md
Sigue el principio fundamental: API se adapta exactamente a BD existente
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

def parse_complete_schema():
    """Parse ESQUEMA_COMPLETO_BD.md para extraer estructura completa"""
    schema_file = Path("ESQUEMA_COMPLETO_BD.md")
    
    if not schema_file.exists():
        print("❌ No se encontró ESQUEMA_COMPLETO_BD.md")
        return None, None
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer tipos enum
    enums = {}
    enum_pattern = r'### (\w+)\n```sql\nCREATE TYPE \w+ AS ENUM \(\n(.*?)\n\);'
    enum_matches = re.findall(enum_pattern, content, re.DOTALL)
    
    for enum_name, enum_values in enum_matches:
        values = [v.strip().strip("'") for v in enum_values.split(',') if v.strip()]
        enums[enum_name] = values
    
    # Extraer tablas
    tables = {}
    current_table = None
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detectar tabla (### nombre_tabla)
        if line.startswith('### ') and not line.startswith('### ') or 'enum' in line.lower():
            table_name = line[4:].strip()
            if table_name not in ['alembic_version'] and not any(x in table_name.lower() for x in ['enum', 'tipo']):
                current_table = table_name
                tables[current_table] = {
                    'columns': [],
                    'constraints': [],
                    'indexes': []
                }
        
        # Detectar columnas en tabla de markdown
        elif current_table and line.startswith('|') and '|' in line and 'Columna' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 4:
                column_name = parts[0]
                data_type = parts[1]
                nullable = parts[2].lower() == 'sí'
                default = parts[3] if parts[3] and parts[3] != '' else None
                
                tables[current_table]['columns'].append({
                    'name': column_name,
                    'type': data_type,
                    'nullable': nullable,
                    'default': default
                })
        
        i += 1
    
    return tables, enums

def map_postgres_to_python_type(pg_type: str, nullable: bool = True) -> Tuple[str, str]:
    """Mapea tipos PostgreSQL a tipos Python y SQLAlchemy"""
    
    # Limpiar tipo
    pg_type = pg_type.lower().strip()
    
    # Mapeo de tipos
    if 'uuid' in pg_type:
        python_type = "UUID"
        sa_type = "UUID(as_uuid=True)"
    elif 'character varying' in pg_type or 'varchar' in pg_type:
        # Extraer longitud
        length_match = re.search(r'\((\d+)\)', pg_type)
        length = length_match.group(1) if length_match else "255"
        python_type = "str"
        sa_type = f"String({length})"
    elif pg_type == 'text':
        python_type = "str"
        sa_type = "Text"
    elif pg_type == 'boolean':
        python_type = "bool"
        sa_type = "Boolean"
    elif 'timestamp with time zone' in pg_type:
        python_type = "datetime"
        sa_type = "DateTime(timezone=True)"
    elif pg_type == 'date':
        python_type = "date"
        sa_type = "Date"
    elif 'integer' in pg_type:
        if 'bigint' in pg_type:
            python_type = "int"
            sa_type = "BigInteger"
        elif 'smallint' in pg_type:
            python_type = "int"
            sa_type = "SmallInteger"
        else:
            python_type = "int"
            sa_type = "Integer"
    elif 'numeric' in pg_type:
        # Extraer precisión y escala
        numeric_match = re.search(r'numeric\((\d+),(\d+)\)', pg_type)
        if numeric_match:
            precision, scale = numeric_match.groups()
            python_type = "Decimal"
            sa_type = f"Numeric({precision}, {scale})"
        else:
            python_type = "Decimal"
            sa_type = "Numeric"
    elif pg_type == 'jsonb':
        python_type = "dict"
        sa_type = "JSONB"
    elif pg_type == 'interval':
        python_type = "timedelta"
        sa_type = "INTERVAL"
    elif 'user-defined' in pg_type.lower():
        # Tipo enum
        python_type = "str"
        sa_type = "String(50)"
    else:
        # Tipo por defecto
        python_type = "str"
        sa_type = "String(255)"
    
    # Hacer opcional si es nullable
    if nullable and python_type not in ["UUID"]:
        python_type = f"Optional[{python_type}]"
    
    return python_type, sa_type

def generate_field_definition(column: dict) -> str:
    """Genera definición de campo SQLModel"""
    name = column['name']
    pg_type = column['type']
    nullable = column['nullable']
    default = column['default']
    
    python_type, sa_type = map_postgres_to_python_type(pg_type, nullable)
    
    # Generar definición del campo
    field_def = f"    {name}: {python_type} = Field("
    
    # Agregar default si existe
    if default and default.strip():
        if 'gen_random_uuid()' in default:
            field_def += "default_factory=uuid4, "
        elif 'now()' in default:
            field_def += "default_factory=datetime.utcnow, "
        elif default.lower() == 'true':
            field_def += "default=True, "
        elif default.lower() == 'false':
            field_def += "default=False, "
        elif default.isdigit():
            field_def += f"default={default}, "
        else:
            field_def += f"default='{default}', " if not default.startswith("'") else f"default={default}, "
    elif nullable:
        field_def += "default=None, "
    
    # Agregar columna SQLAlchemy
    field_def += f"sa_column=Column({sa_type}"
    
    # Agregar constraints
    if not nullable:
        field_def += ", nullable=False"
    
    if name == 'id' and 'uuid' in pg_type:
        field_def += ", primary_key=True"
        if 'gen_random_uuid()' in str(default):
            field_def += ", server_default=text('gen_random_uuid()')"
    
    field_def += "))"
    
    return field_def

def generate_model_class(table_name: str, table_info: dict) -> str:
    """Genera clase SQLModel completa"""
    
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    
    # Imports necesarios
    imports = [
        "from datetime import date, datetime, timedelta",
        "from decimal import Decimal",
        "from typing import Optional, Dict",
        "from uuid import UUID, uuid4",
        "",
        "from sqlmodel import SQLModel, Field",
        "from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, BigInteger, SmallInteger",
        "from sqlalchemy import Numeric, Date, UUID as SA_UUID, JSONB, INTERVAL, text",
        "from sqlalchemy.dialects.postgresql import UUID as PG_UUID"
    ]
    
    # Generar clase
    model_lines = [
        f"class {class_name}(SQLModel, table=True):",
        f'    """Modelo para tabla {table_name} - Alineado exactamente con esquema real"""',
        f'    __tablename__ = "{table_name}"',
        "",
        "    # Campos exactos del esquema PostgreSQL"
    ]
    
    # Generar campos
    for column in table_info['columns']:
        field_def = generate_field_definition(column)
        model_lines.append(field_def)
    
    return '\n'.join(imports) + '\n\n' + '\n'.join(model_lines)

def update_module_models():
    """Actualiza modelos en cada módulo basado en el esquema completo"""
    
    print("🚀 ACTUALIZANDO MODELOS DESDE ESQUEMA COMPLETO")
    print("="*60)
    
    # Parse esquema
    tables, enums = parse_complete_schema()
    if not tables:
        print("❌ No se pudo parsear el esquema")
        return
    
    print(f"✅ Parseadas {len(tables)} tablas y {len(enums)} enums")
    
    # Mapeo de tablas a módulos
    module_mapping = {
        # Auth
        'usuarios': 'auth',
        'roles': 'auth',
        'permisos': 'auth',
        'usuarios_roles': 'auth',
        'roles_permisos': 'auth',
        'auditoria_roles_usuarios': 'auth',
        
        # Vehículos
        'vehiculos': 'vehiculos',
        'tipos_vehiculo': 'vehiculos',
        'configuraciones_eje': 'vehiculos',
        'posiciones_neumatico': 'vehiculos',
        'registros_odometro': 'vehiculos',
        
        # Neumáticos
        'neumaticos': 'neumaticos',
        'fabricantes_neumatico': 'neumaticos',
        'modelos_neumatico': 'neumaticos',
        'especificaciones_desgaste': 'neumaticos',
        'modelos_posiciones_permitidas': 'neumaticos',
        'parametros_rendimiento_esperado_modelo': 'neumaticos',
        
        # Catálogos
        'proveedores': 'catalogos',
        'almacenes': 'catalogos',
        'motivos_desecho': 'catalogos',
        'parametros_inventario': 'catalogos',
        'parametros_sistema': 'catalogos',
        
        # Bitácoras
        'bitacora_operaciones': 'bitacoras',
        'bitacora_operaciones_neumaticos': 'bitacoras',
        'bitacora_mantenimiento': 'bitacoras',
        
        # Eventos
        'eventos_neumaticos': 'eventos',
        'historial_estados_neumaticos': 'eventos',
        'mediciones_profundidad': 'eventos',
        
        # Garantías
        'garantias_neumaticos': 'garantias',
        
        # Alertas
        'alertas': 'alertas',
        
        # Auditoría
        'auditoria_log': 'auditoria',
        'configuracion_auditoria': 'auditoria',
        'errores_aplicacion': 'auditoria',
        
        # Rutas
        'rutas': 'rutas',
        'tipos_ruta': 'rutas',
        
        # Sistema
        'tareas_programadas': 'sistema'
    }
    
    # Agrupar tablas por módulo
    modules = {}
    for table_name, table_info in tables.items():
        if table_name == 'alembic_version':
            continue
            
        module_name = module_mapping.get(table_name, 'otros')
        if module_name not in modules:
            modules[module_name] = []
        modules[module_name].append((table_name, table_info))
    
    # Generar archivos por módulo
    for module_name, module_tables in modules.items():
        print(f"\n📝 Actualizando módulo: {module_name}")
        
        # Crear directorio si no existe
        module_dir = Path(f"ges_neu_api/modules/{module_name}")
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar archivo models_updated.py
        models_file = module_dir / "models_updated.py"
        
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(f'"""\nModelos actualizados para {module_name}\nBasado en ESQUEMA_COMPLETO_BD.md - Alineación exacta con BD PostgreSQL\nGenerado automáticamente - NO MODIFICAR MANUALMENTE\n"""\n\n')
            
            # Imports globales
            f.write("from datetime import date, datetime, timedelta\n")
            f.write("from decimal import Decimal\n")
            f.write("from typing import Optional, Dict\n")
            f.write("from uuid import UUID, uuid4\n\n")
            f.write("from sqlmodel import SQLModel, Field\n")
            f.write("from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, BigInteger, SmallInteger\n")
            f.write("from sqlalchemy import Numeric, Date, JSONB, INTERVAL, text\n")
            f.write("from sqlalchemy.dialects.postgresql import UUID as PG_UUID\n\n")
            
            # Generar cada modelo
            for table_name, table_info in module_tables:
                print(f"  • {table_name}")
                
                class_name = ''.join(word.capitalize() for word in table_name.split('_'))
                
                f.write(f"class {class_name}(SQLModel, table=True):\n")
                f.write(f'    """Modelo para tabla {table_name} - Alineado exactamente con esquema real"""\n')
                f.write(f'    __tablename__ = "{table_name}"\n\n')
                
                # Generar campos
                for column in table_info['columns']:
                    field_def = generate_field_definition(column)
                    f.write(field_def + '\n')
                
                f.write('\n\n')
        
        print(f"✅ Archivo generado: {models_file}")
    
    print("\n" + "="*60)
    print("🎉 ACTUALIZACIÓN COMPLETADA")
    print(f"📋 Módulos actualizados: {len(modules)}")
    for module_name in modules.keys():
        print(f"  • {module_name}: {len(modules[module_name])} tablas")
    
    print("\n⚠️  PRÓXIMOS PASOS:")
    print("  1. Revisar archivos models_updated.py generados")
    print("  2. Reemplazar modelos existentes con versiones actualizadas")
    print("  3. Ejecutar pruebas para validar alineación")
    print("  4. Verificar que la API arranca sin errores")

if __name__ == "__main__":
    update_module_models()
