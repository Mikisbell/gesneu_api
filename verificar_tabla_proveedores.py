#!/usr/bin/env python3
"""
Verificar estructura y contenido de la tabla proveedores
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def verificar_tabla_proveedores():
    """Verifica la estructura y contenido de la tabla proveedores"""
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='ges_neu_bd',
            user='postgres',
            password='B3ll1c0s'
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 VERIFICANDO TABLA PROVEEDORES")
        print("=" * 40)
        
        # 1. Verificar si la tabla existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'proveedores'
            );
        """)
        tabla_existe = cursor.fetchone()[0]
        print(f"📋 Tabla 'proveedores' existe: {tabla_existe}")
        
        if not tabla_existe:
            print("❌ ERROR: La tabla 'proveedores' no existe en la BD")
            return False
        
        # 2. Verificar estructura de la tabla
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'proveedores'
            ORDER BY ordinal_position;
        """)
        
        columnas = cursor.fetchall()
        print(f"\n📊 Estructura de la tabla ({len(columnas)} columnas):")
        for col in columnas:
            print(f"   • {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # 3. Verificar si hay datos en la tabla
        cursor.execute("SELECT COUNT(*) FROM proveedores;")
        count = cursor.fetchone()[0]
        print(f"\n📈 Registros en la tabla: {count}")
        
        # 4. Verificar ENUMs relacionados
        cursor.execute("""
            SELECT typname, enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE typname = 'tipoproveedorenum'
            ORDER BY enumsortorder;
        """)
        
        enum_valores = cursor.fetchall()
        print(f"\n🏷️  ENUM tipoproveedorenum ({len(enum_valores)} valores):")
        for enum_val in enum_valores:
            print(f"   • {enum_val['enumlabel']}")
        
        # 5. Mostrar algunos registros de ejemplo si existen
        if count > 0:
            cursor.execute("SELECT id, nombre, tipo, activo FROM proveedores LIMIT 3;")
            ejemplos = cursor.fetchall()
            print(f"\n📋 Ejemplos de registros:")
            for ejemplo in ejemplos:
                print(f"   • ID: {ejemplo['id']}, Nombre: {ejemplo['nombre']}, Tipo: {ejemplo['tipo']}, Activo: {ejemplo['activo']}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Verificación de tabla completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR al verificar tabla: {str(e)}")
        return False

if __name__ == "__main__":
    verificar_tabla_proveedores()
