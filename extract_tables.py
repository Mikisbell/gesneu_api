import asyncio
import asyncpg

async def extract_tables():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='B3ll1c0s',
            database='ges_neu_bd'
        )
        print('✅ Conexión exitosa a ges_neu_bd')
        
        # Obtener lista de tablas
        tables = await conn.fetch('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        ''')
        
        print(f'📋 Encontradas {len(tables)} tablas:')
        
        # Crear archivo con estructura de todas las tablas
        with open('estructura_tablas_completa.md', 'w', encoding='utf-8') as f:
            f.write('# Estructura Completa de Tablas - ges_neu_bd\n\n')
            f.write(f'Total de tablas: {len(tables)}\n\n')
            
            for table in tables:
                table_name = table['table_name']
                print(f'  📊 Procesando: {table_name}')
                
                # Obtener estructura de la tabla
                columns = await conn.fetch('''
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
                    AND table_name = $1
                    ORDER BY ordinal_position
                ''', table_name)
                
                # Escribir estructura al archivo
                f.write(f'## {table_name}\n\n')
                f.write('| Columna | Tipo | Nulable | Por Defecto |\n')
                f.write('|---------|------|---------|-------------|\n')
                
                for col in columns:
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
                
                f.write('\n---\n\n')
        
        await conn.close()
        print('✅ Estructura extraída y guardada en: estructura_tablas_completa.md')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    asyncio.run(extract_tables())
