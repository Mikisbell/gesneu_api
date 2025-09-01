import psycopg2
import json

def extract_schema():
    try:
        # Conexión a PostgreSQL
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='B3ll1c0s',
            database='ges_neu_bd'
        )
        cursor = conn.cursor()
        
        print('✅ Conectado a ges_neu_bd')
        
        # Obtener todas las tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f'📋 Encontradas {len(tables)} tablas')
        
        schema_data = {}
        
        for (table_name,) in tables:
            print(f'  📊 {table_name}')
            
            # Obtener columnas de la tabla
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    udt_name
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            schema_data[table_name] = []
            for col in columns:
                schema_data[table_name].append({
                    'column_name': col[0],
                    'data_type': col[1],
                    'is_nullable': col[2],
                    'column_default': col[3],
                    'character_maximum_length': col[4],
                    'numeric_precision': col[5],
                    'numeric_scale': col[6],
                    'udt_name': col[7]
                })
        
        # Guardar en JSON
        with open('schema_completo.json', 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Crear archivo markdown
        with open('ESQUEMA_COMPLETO.md', 'w', encoding='utf-8') as f:
            f.write('# Esquema Completo - Base de Datos ges_neu_bd\n\n')
            f.write(f'Total de tablas: {len(tables)}\n\n')
            
            for table_name in sorted(schema_data.keys()):
                f.write(f'## {table_name}\n\n')
                f.write('| Columna | Tipo | Nulable | Por Defecto |\n')
                f.write('|---------|------|---------|-------------|\n')
                
                for col in schema_data[table_name]:
                    nullable = 'Sí' if col['is_nullable'] == 'YES' else 'No'
                    default = col['column_default'] or ''
                    data_type = col['data_type']
                    
                    if col['character_maximum_length']:
                        data_type += f"({col['character_maximum_length']})"
                    elif col['numeric_precision']:
                        if col['numeric_scale']:
                            data_type += f"({col['numeric_precision']},{col['numeric_scale']})"
                        else:
                            data_type += f"({col['numeric_precision']})"
                    
                    f.write(f"| {col['column_name']} | {data_type} | {nullable} | {default} |\n")
                
                f.write('\n')
        
        cursor.close()
        conn.close()
        
        print('✅ Archivos generados:')
        print('  - schema_completo.json')
        print('  - ESQUEMA_COMPLETO.md')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    extract_schema()
