#!/usr/bin/env python3
"""
Script para extraer la estructura completa de todas las tablas de la base de datos ges_neu_bd
"""
import asyncio
import asyncpg
import json
from datetime import datetime

# Configuración de conexión
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'B3ll1c0s',
    'database': 'ges_neu_bd'
}

async def get_all_tables(conn):
    """Obtiene la lista de todas las tablas en el esquema public"""
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name;
    """
    result = await conn.fetch(query)
    return [row['table_name'] for row in result]

async def get_table_structure(conn, table_name):
    """Obtiene la estructura detallada de una tabla específica"""
    query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length,
        numeric_precision,
        numeric_scale,
        udt_name,
        ordinal_position
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = $1
    ORDER BY ordinal_position;
    """
    result = await conn.fetch(query, table_name)
    return [dict(row) for row in result]

async def get_table_constraints(conn, table_name):
    """Obtiene las restricciones de una tabla"""
    query = """
    SELECT 
        tc.constraint_name,
        tc.constraint_type,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name,
        cc.check_clause
    FROM information_schema.table_constraints tc
    LEFT JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
    LEFT JOIN information_schema.constraint_column_usage ccu 
        ON tc.constraint_name = ccu.constraint_name
    LEFT JOIN information_schema.check_constraints cc 
        ON tc.constraint_name = cc.constraint_name
    WHERE tc.table_schema = 'public' 
    AND tc.table_name = $1
    ORDER BY tc.constraint_type, tc.constraint_name;
    """
    result = await conn.fetch(query, table_name)
    return [dict(row) for row in result]

async def get_table_indexes(conn, table_name):
    """Obtiene los índices de una tabla"""
    query = """
    SELECT 
        indexname,
        indexdef
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND tablename = $1
    ORDER BY indexname;
    """
    result = await conn.fetch(query, table_name)
    return [dict(row) for row in result]

async def get_enum_values(conn):
    """Obtiene todos los tipos enum y sus valores"""
    query = """
    SELECT 
        t.typname as enum_name,
        e.enumlabel as enum_value,
        e.enumsortorder
    FROM pg_type t 
    JOIN pg_enum e ON t.oid = e.enumtypid  
    JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
    WHERE n.nspname = 'public'
    ORDER BY t.typname, e.enumsortorder;
    """
    result = await conn.fetch(query)
    
    enums = {}
    for row in result:
        enum_name = row['enum_name']
        if enum_name not in enums:
            enums[enum_name] = []
        enums[enum_name].append(row['enum_value'])
    
    return enums

async def extract_complete_schema():
    """Extrae el esquema completo de la base de datos"""
    print("🔍 Conectando a la base de datos ges_neu_bd...")
    
    try:
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        print("✅ Conexión establecida")
        
        # Obtener información general
        db_version = await conn.fetchval("SELECT version()")
        current_db = await conn.fetchval("SELECT current_database()")
        
        print(f"📊 Base de datos: {current_db}")
        print(f"🐘 PostgreSQL: {db_version[:50]}...")
        
        # Obtener todas las tablas
        print("\n🔍 Obteniendo lista de tablas...")
        tables = await get_all_tables(conn)
        print(f"📋 Encontradas {len(tables)} tablas")
        
        # Obtener tipos enum
        print("\n🔍 Obteniendo tipos enum...")
        enums = await get_enum_values(conn)
        print(f"📝 Encontrados {len(enums)} tipos enum")
        
        # Estructura completa
        complete_schema = {
            'metadata': {
                'database': current_db,
                'extraction_date': datetime.now().isoformat(),
                'postgresql_version': db_version,
                'total_tables': len(tables)
            },
            'enums': enums,
            'tables': {}
        }
        
        # Extraer estructura de cada tabla
        print("\n🔍 Extrayendo estructura de tablas...")
        for i, table_name in enumerate(tables, 1):
            print(f"  [{i:2d}/{len(tables)}] Procesando tabla: {table_name}")
            
            # Estructura de columnas
            columns = await get_table_structure(conn, table_name)
            
            # Restricciones
            constraints = await get_table_constraints(conn, table_name)
            
            # Índices
            indexes = await get_table_indexes(conn, table_name)
            
            complete_schema['tables'][table_name] = {
                'columns': columns,
                'constraints': constraints,
                'indexes': indexes
            }
        
        await conn.close()
        
        # Guardar en archivo JSON
        output_file = 'complete_database_schema.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_schema, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Esquema completo guardado en: {output_file}")
        
        # Generar resumen
        print("\n" + "="*70)
        print("📊 RESUMEN DEL ESQUEMA EXTRAÍDO")
        print("="*70)
        print(f"Base de datos: {current_db}")
        print(f"Total de tablas: {len(tables)}")
        print(f"Tipos enum: {len(enums)}")
        
        print(f"\n📋 TABLAS ENCONTRADAS:")
        for table in sorted(tables):
            table_info = complete_schema['tables'][table]
            col_count = len(table_info['columns'])
            constraint_count = len(table_info['constraints'])
            index_count = len(table_info['indexes'])
            print(f"  • {table:<30} ({col_count:2d} columnas, {constraint_count:2d} restricciones, {index_count:2d} índices)")
        
        if enums:
            print(f"\n🏷️  TIPOS ENUM:")
            for enum_name, values in enums.items():
                print(f"  • {enum_name}: {', '.join(values)}")
        
        print(f"\n💾 Archivo generado: {output_file}")
        print("🎉 Extracción completada exitosamente!")
        
        return complete_schema
        
    except Exception as e:
        print(f"❌ Error durante la extracción: {e}")
        return None

async def generate_markdown_schema(schema_data):
    """Genera un archivo markdown con el esquema"""
    if not schema_data:
        return
    
    output_file = 'ESQUEMA_COMPLETO_BD.md'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Esquema Completo de Base de Datos - ges_neu_bd\n\n")
        f.write(f"**Fecha de extracción:** {schema_data['metadata']['extraction_date']}\n")
        f.write(f"**Base de datos:** {schema_data['metadata']['database']}\n")
        f.write(f"**PostgreSQL:** {schema_data['metadata']['postgresql_version'][:100]}\n")
        f.write(f"**Total de tablas:** {schema_data['metadata']['total_tables']}\n\n")
        
        # Tipos enum
        if schema_data['enums']:
            f.write("## Tipos Enum\n\n")
            for enum_name, values in schema_data['enums'].items():
                f.write(f"### {enum_name}\n")
                f.write("```sql\n")
                f.write(f"CREATE TYPE {enum_name} AS ENUM (\n")
                for i, value in enumerate(values):
                    comma = "," if i < len(values) - 1 else ""
                    f.write(f"    '{value}'{comma}\n")
                f.write(");\n```\n\n")
        
        # Tablas
        f.write("## Tablas\n\n")
        for table_name, table_info in schema_data['tables'].items():
            f.write(f"### {table_name}\n\n")
            
            # Columnas
            f.write("#### Columnas\n\n")
            f.write("| Columna | Tipo | Nulable | Por Defecto | Descripción |\n")
            f.write("|---------|------|---------|-------------|-------------|\n")
            
            for col in table_info['columns']:
                nullable = "Sí" if col['is_nullable'] == 'YES' else "No"
                default = col['column_default'] or ""
                data_type = col['data_type']
                if col['character_maximum_length']:
                    data_type += f"({col['character_maximum_length']})"
                elif col['numeric_precision']:
                    if col['numeric_scale']:
                        data_type += f"({col['numeric_precision']},{col['numeric_scale']})"
                    else:
                        data_type += f"({col['numeric_precision']})"
                
                f.write(f"| {col['column_name']} | {data_type} | {nullable} | {default} |  |\n")
            
            # Restricciones
            if table_info['constraints']:
                f.write(f"\n#### Restricciones\n\n")
                for constraint in table_info['constraints']:
                    f.write(f"- **{constraint['constraint_name']}** ({constraint['constraint_type']})")
                    if constraint['column_name']:
                        f.write(f" - Columna: {constraint['column_name']}")
                    if constraint['foreign_table_name']:
                        f.write(f" - Referencia: {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
                    if constraint['check_clause']:
                        f.write(f" - Condición: {constraint['check_clause']}")
                    f.write("\n")
            
            # Índices
            if table_info['indexes']:
                f.write(f"\n#### Índices\n\n")
                for index in table_info['indexes']:
                    f.write(f"- **{index['indexname']}**\n")
                    f.write(f"  ```sql\n  {index['indexdef']}\n  ```\n")
            
            f.write("\n---\n\n")
    
    print(f"📄 Esquema en Markdown guardado en: {output_file}")

if __name__ == "__main__":
    print("🚀 EXTRACTOR DE ESQUEMA COMPLETO - BASE DE DATOS GES_NEU_BD")
    print("="*70)
    
    # Ejecutar extracción
    schema = asyncio.run(extract_complete_schema())
    
    if schema:
        # Generar también en formato Markdown
        asyncio.run(generate_markdown_schema(schema))
        
        print("\n🎯 ARCHIVOS GENERADOS:")
        print("  • complete_database_schema.json (formato JSON completo)")
        print("  • ESQUEMA_COMPLETO_BD.md (formato Markdown legible)")
        print("\n✅ Proceso completado exitosamente!")
    else:
        print("\n❌ No se pudo extraer el esquema")
