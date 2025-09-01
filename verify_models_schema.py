"""
Script para verificar que todos los modelos coincidan exactamente con el esquema de la BD
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        # Usar valores por defecto si no están en .env
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'ges_neu_bd'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la BD: {e}")
        print("Verificar que PostgreSQL este corriendo y las credenciales sean correctas")
        return None

def get_table_schema(conn, table_name):
    """Obtener esquema detallado de una tabla"""
    cursor = conn.cursor()
    
    # Obtener columnas con tipos de datos
    query = """
    SELECT 
        column_name,
        data_type,
        character_maximum_length,
        numeric_precision,
        numeric_scale,
        is_nullable,
        column_default,
        ordinal_position
    FROM information_schema.columns 
    WHERE table_name = %s AND table_schema = 'public'
    ORDER BY ordinal_position;
    """
    
    cursor.execute(query, (table_name,))
    columns = cursor.fetchall()
    
    # Obtener claves primarias
    pk_query = """
    SELECT column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = %s 
        AND tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = 'public';
    """
    
    cursor.execute(pk_query, (table_name,))
    primary_keys = [row['column_name'] for row in cursor.fetchall()]
    
    # Obtener claves foráneas
    fk_query = """
    SELECT 
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_name = %s
        AND tc.table_schema = 'public';
    """
    
    cursor.execute(fk_query, (table_name,))
    foreign_keys = cursor.fetchall()
    
    return {
        'columns': columns,
        'primary_keys': primary_keys,
        'foreign_keys': foreign_keys
    }

def verify_all_models():
    """Verificar todos los modelos contra la BD"""
    conn = get_db_connection()
    if not conn:
        return
    
    # Lista de todas las 36 tablas
    tables_to_verify = [
        # Autenticación
        'usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos',
        
        # Vehículos
        'vehiculos', 'tipos_vehiculo', 'registros_odometro',
        
        # Neumáticos y relacionados
        'neumaticos', 'modelos_neumatico', 'fabricantes_neumatico', 
        'posiciones_neumatico', 'configuraciones_eje',
        
        # Inventario
        'inventario_neumaticos', 'movimientos_inventario', 'almacenes', 
        'parametros_inventario',
        
        # Catálogos
        'proveedores', 'disenios', 'motivos_desecho',
        
        # Rutas
        'rutas', 'tipos_ruta',
        
        # Sistema
        'parametros_sistema', 'tareas_programadas',
        
        # Bitácoras
        'bitacora_mantenimiento', 'bitacora_operaciones', 
        'bitacora_operaciones_neumaticos',
        
        # Auditoría
        'auditoria_log', 'configuracion_auditoria', 'errores_aplicacion',
        
        # Eventos y mediciones
        'eventos_neumaticos', 'mediciones_profundidad', 
        'especificaciones_desgaste', 'historial_estados_neumaticos',
        
        # Garantías y alertas
        'garantias_neumaticos', 'alertas',
        
        # Configuración avanzada
        'parametros_rendimiento_esperado_modelo', 'modelos_posiciones_permitidas'
    ]
    
    print("=== VERIFICACION DE MODELOS VS ESQUEMA BD ===\n")
    
    missing_tables = []
    verified_tables = []
    
    for table_name in tables_to_verify:
        try:
            schema = get_table_schema(conn, table_name)
            if schema['columns']:
                verified_tables.append(table_name)
                print(f"✓ {table_name}: {len(schema['columns'])} columnas")
                
                # Mostrar detalles de columnas críticas
                for col in schema['columns'][:3]:  # Solo primeras 3 columnas
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"  - {col['column_name']}: {col['data_type']} {nullable}")
                    
                if len(schema['columns']) > 3:
                    print(f"  ... y {len(schema['columns']) - 3} columnas más")
                print()
            else:
                missing_tables.append(table_name)
                print(f"✗ {table_name}: TABLA NO ENCONTRADA")
                
        except Exception as e:
            missing_tables.append(table_name)
            print(f"✗ {table_name}: ERROR - {e}")
    
    print(f"\n=== RESUMEN ===")
    print(f"Tablas verificadas: {len(verified_tables)}/36")
    print(f"Tablas faltantes: {len(missing_tables)}")
    
    if missing_tables:
        print(f"\nTablas faltantes:")
        for table in missing_tables:
            print(f"  - {table}")
    
    conn.close()
    return len(verified_tables) == 36

if __name__ == "__main__":
    success = verify_all_models()
    if success:
        print("\nTODOS LOS MODELOS VERIFICADOS EXITOSAMENTE!")
    else:
        print("\nALGUNOS MODELOS REQUIEREN ATENCION")
