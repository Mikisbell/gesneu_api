#!/usr/bin/env python3
"""
Generador de modelos SQLModel basado en ESQUEMA_BD_REAL.md
Sigue el principio fundamental: API se adapta a BD existente, NO al revés
"""
import re
from pathlib import Path

def parse_schema_file():
    """Parse el archivo ESQUEMA_BD_REAL.md para extraer estructura de tablas"""
    schema_file = Path("ESQUEMA_BD_REAL.md")
    
    if not schema_file.exists():
        print("❌ No se encontró ESQUEMA_BD_REAL.md")
        return None
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer información de tablas
    tables = {}
    current_table = None
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        # Detectar nombre de tabla (#### nombre_tabla)
        if line.startswith('#### ') and not line.startswith('#### MÓDULO'):
            current_table = line[4:].strip()
            tables[current_table] = {
                'columns': [],
                'constraints': []
            }
        
        # Detectar columnas (- campo: tipo info)
        elif line.startswith('- ') and current_table and ':' in line:
            column_info = line[2:].strip()
            tables[current_table]['columns'].append(column_info)
        
        # Detectar constraints (- CONSTRAINT info)
        elif line.startswith('- ') and current_table and ('UNIQUE' in line or 'PRIMARY KEY' in line or 'FK' in line):
            constraint_info = line[2:].strip()
            tables[current_table]['constraints'].append(constraint_info)
    
    return tables

def generate_sqlmodel_field(column_info):
    """Genera un campo SQLModel basado en la información de columna"""
    # Parsear información de columna
    parts = column_info.split(':')
    if len(parts) < 2:
        return None
    
    field_name = parts[0].strip()
    type_info = parts[1].strip()
    
    # Determinar tipo Python y SQLAlchemy
    python_type = "str"
    sa_column = "String(255)"
    nullable = True
    default = None
    
    # Mapeo de tipos
    if "UUID" in type_info:
        python_type = "UUID"
        sa_column = "PG_UUID(as_uuid=True)"
        if "(PK)" in type_info:
            sa_column += ", primary_key=True, server_default=text('gen_random_uuid()')"
        elif "FK(" in type_info:
            # Extraer tabla referenciada
            fk_match = re.search(r'FK\(([^)]+)\)', type_info)
            if fk_match:
                ref_table = fk_match.group(1)
                sa_column += f", ForeignKey('{ref_table}')"
    
    elif "String(" in type_info:
        length_match = re.search(r'String\((\d+)\)', type_info)
        if length_match:
            length = length_match.group(1)
            sa_column = f"String({length})"
    
    elif "Text" in type_info:
        sa_column = "Text"
    
    elif "Boolean" in type_info:
        python_type = "bool"
        sa_column = "Boolean"
    
    elif "DateTime" in type_info:
        python_type = "datetime"
        sa_column = "TIMESTAMP"
        if "timezone=True" in type_info:
            sa_column = "DateTime(timezone=True)"
    
    elif "Date" in type_info:
        python_type = "date"
        sa_column = "Date"
    
    elif "Integer" in type_info:
        python_type = "int"
        sa_column = "Integer"
    
    elif "Numeric(" in type_info:
        python_type = "Decimal"
        numeric_match = re.search(r'Numeric\((\d+),(\d+)\)', type_info)
        if numeric_match:
            precision, scale = numeric_match.groups()
            sa_column = f"Numeric({precision}, {scale})"
    
    # Determinar nullabilidad
    if "NOT NULL" in type_info:
        nullable = False
    
    # Determinar default
    if "DEFAULT" in type_info:
        if "DEFAULT true" in type_info:
            default = "True"
        elif "DEFAULT false" in type_info:
            default = "False"
        elif "DEFAULT now()" in type_info:
            default = "datetime.utcnow"
        elif "DEFAULT 0" in type_info:
            default = "0"
    
    # Generar código del campo
    if nullable and python_type != "UUID":
        python_type = f"Optional[{python_type}]"
    
    field_code = f"    {field_name}: {python_type} = Field("
    
    if default:
        if default == "datetime.utcnow":
            field_code += f"default_factory={default}, "
        else:
            field_code += f"default={default}, "
    elif nullable:
        field_code += "default=None, "
    
    field_code += f"sa_column=Column({sa_column}"
    
    if not nullable:
        field_code += ", nullable=False"
    
    if "UNIQUE" in type_info:
        field_code += ", unique=True"
    
    field_code += "))"
    
    return field_code

def generate_model_file(table_name, table_info, module_name):
    """Genera un archivo de modelo SQLModel para una tabla"""
    
    # Mapeo de tablas a módulos
    module_mapping = {
        'usuarios': 'auth',
        'roles': 'auth', 
        'permisos': 'auth',
        'usuarios_roles': 'auth',
        'roles_permisos': 'auth',
        'auditoria_roles_usuarios': 'auth',
        'vehiculos': 'vehiculos',
        'tipos_vehiculo': 'vehiculos',
        'configuraciones_eje': 'vehiculos',
        'posiciones_neumatico': 'vehiculos',
        'registros_odometro': 'vehiculos',
        'neumaticos': 'neumaticos',
        'fabricantes_neumatico': 'neumaticos',
        'modelos_neumatico': 'neumaticos',
        'proveedores': 'catalogos',
        'almacenes': 'catalogos',
        'motivos_desecho': 'catalogos',
        'parametros_inventario': 'catalogos'
    }
    
    actual_module = module_mapping.get(table_name, module_name)
    
    # Generar imports
    imports = [
        "from datetime import date, datetime",
        "from decimal import Decimal", 
        "from typing import Optional",
        "from uuid import UUID, uuid4",
        "",
        "from sqlmodel import SQLModel, Field",
        "from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP",
        "from sqlalchemy.dialects.postgresql import UUID as PG_UUID",
        "from sqlalchemy import text"
    ]
    
    # Generar clase del modelo
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    
    model_code = [
        f'class {class_name}(SQLModel, table=True):',
        f'    """Modelo para tabla {table_name} - Alineado con esquema real de BD"""',
        f'    __tablename__ = "{table_name}"',
        '',
        '    # Campos exactos del esquema real'
    ]
    
    # Generar campos
    for column_info in table_info['columns']:
        field_code = generate_sqlmodel_field(column_info)
        if field_code:
            model_code.append(field_code)
    
    # Agregar constraints si existen
    if table_info['constraints']:
        model_code.extend([
            '',
            '    __table_args__ = ('
        ])
        
        for constraint in table_info['constraints']:
            if 'UNIQUE(' in constraint:
                # Extraer campos del UNIQUE
                unique_match = re.search(r'UNIQUE\(([^)]+)\)', constraint)
                if unique_match:
                    fields = unique_match.group(1)
                    model_code.append(f'        UniqueConstraint({fields}),')
            elif 'PRIMARY KEY(' in constraint:
                # Extraer campos del PRIMARY KEY
                pk_match = re.search(r'PRIMARY KEY\(([^)]+)\)', constraint)
                if pk_match:
                    fields = pk_match.group(1)
                    model_code.append(f'        # Primary key: {fields}')
        
        model_code.append('    )')
    
    # Combinar todo
    full_code = '\n'.join(imports) + '\n\n' + '\n'.join(model_code)
    
    return full_code

def main():
    """Función principal"""
    print("🚀 GENERADOR DE MODELOS SQLMODEL DESDE ESQUEMA REAL")
    print("="*60)
    
    # Parsear esquema
    print("📖 Parseando ESQUEMA_BD_REAL.md...")
    tables = parse_schema_file()
    
    if not tables:
        print("❌ No se pudo parsear el esquema")
        return
    
    print(f"✅ Encontradas {len(tables)} tablas")
    
    # Generar modelos por módulo
    modules = {
        'auth': ['usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos', 'auditoria_roles_usuarios'],
        'vehiculos': ['vehiculos', 'tipos_vehiculo', 'configuraciones_eje', 'posiciones_neumatico', 'registros_odometro'],
        'neumaticos': ['neumaticos', 'fabricantes_neumatico', 'modelos_neumatico'],
        'catalogos': ['proveedores', 'almacenes', 'motivos_desecho', 'parametros_inventario']
    }
    
    for module_name, table_list in modules.items():
        print(f"\n📝 Generando modelos para módulo: {module_name}")
        
        # Crear directorio si no existe
        module_dir = Path(f"ges_neu_api/modules/{module_name}")
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar archivo de modelos
        models_file = module_dir / "models_generated.py"
        
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(f'"""\nModelos generados automáticamente para {module_name}\nBasado en ESQUEMA_BD_REAL.md - NO MODIFICAR MANUALMENTE\n"""\n\n')
            
            for table_name in table_list:
                if table_name in tables:
                    print(f"  • {table_name}")
                    model_code = generate_model_file(table_name, tables[table_name], module_name)
                    f.write(model_code + '\n\n')
        
        print(f"✅ Archivo generado: {models_file}")
    
    print("\n" + "="*60)
    print("🎉 GENERACIÓN COMPLETADA")
    print("📋 Archivos generados:")
    for module_name in modules.keys():
        print(f"  • ges_neu_api/modules/{module_name}/models_generated.py")
    
    print("\n⚠️  IMPORTANTE:")
    print("  • Estos modelos están alineados exactamente con el esquema real")
    print("  • NO modificar manualmente - regenerar si hay cambios en BD")
    print("  • Usar estos modelos como referencia para corregir modelos existentes")

if __name__ == "__main__":
    main()
