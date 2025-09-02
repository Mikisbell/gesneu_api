#!/usr/bin/env python3
"""
Test simple de conexión a PostgreSQL sin asyncpg
"""

import psycopg2
from psycopg2 import sql

# Configuración de BD desde .env
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ges_neu_bd',
    'user': 'postgres',
    'password': 'B3ll1c0s'
}

def test_db_connection():
    """Prueba la conexión a PostgreSQL usando psycopg2"""
    print("🔍 VERIFICANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Intentar conexión
        print(f"📡 Conectando a: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"📊 Base de datos: {DB_CONFIG['database']}")
        print(f"👤 Usuario: {DB_CONFIG['user']}")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        print("✅ Conexión exitosa a PostgreSQL")
        
        cursor = conn.cursor()
        
        # Verificar versión
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"📋 Versión: {version}")
        
        # Verificar si la BD existe y tiene tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        if len(tables) > 0:
            print("✅ Base de datos contiene tablas:")
            for i, table in enumerate(tables[:10]):  # Mostrar primeras 10
                print(f"   {i+1}. {table[0]}")
            if len(tables) > 10:
                print(f"   ... y {len(tables) - 10} más")
        else:
            print("❌ Base de datos vacía - no hay tablas")
        
        # Verificar tablas críticas del esquema
        critical_tables = [
            'usuarios', 'roles', 'permisos',
            'vehiculos', 'tipos_vehiculo',
            'neumaticos', 'fabricantes_neumatico',
            'proveedores', 'almacenes'
        ]
        
        print("\n🔍 VERIFICANDO TABLAS CRÍTICAS:")
        for table in critical_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table,))
            
            exists = cursor.fetchone()[0]
            status = "✅" if exists else "❌"
            print(f"{status} {table}")
        
        # Verificar datos en tabla usuarios
        try:
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            user_count = cursor.fetchone()[0]
            print(f"\n📊 Usuarios en BD: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT username FROM usuarios LIMIT 5")
                users = cursor.fetchall()
                print("👥 Usuarios encontrados:")
                for user in users:
                    print(f"   - {user[0]}")
        except Exception as e:
            print(f"❌ Error consultando usuarios: {e}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        if "database" in str(e) and "does not exist" in str(e):
            print("❌ Error: Base de datos 'ges_neu_bd' no existe")
            print("💡 Solución: Crear la base de datos o verificar el nombre")
        elif "authentication failed" in str(e):
            print("❌ Error: Credenciales incorrectas")
            print("💡 Solución: Verificar usuario/contraseña en .env")
        elif "could not connect" in str(e):
            print("❌ Error: No se puede conectar a PostgreSQL")
            print("💡 Solución: Verificar que PostgreSQL esté ejecutándose")
        else:
            print(f"❌ Error de conexión: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        print(f"💡 Tipo de error: {type(e).__name__}")
        return False

def main():
    print("🚀 DIAGNÓSTICO DE BASE DE DATOS - API GESNEU")
    print("=" * 60)
    
    # Probar conexión
    connection_ok = test_db_connection()
    
    print("\n" + "=" * 60)
    if connection_ok:
        print("🎯 DIAGNÓSTICO COMPLETADO - CONEXIÓN OK")
        print("💡 La base de datos está disponible y contiene datos")
    else:
        print("🚨 DIAGNÓSTICO COMPLETADO - PROBLEMAS DETECTADOS")
        print("💡 Revisar configuración de PostgreSQL y credenciales")

if __name__ == "__main__":
    main()
