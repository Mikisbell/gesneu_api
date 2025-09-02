#!/usr/bin/env python3
"""
Script para verificar la conexión a la base de datos PostgreSQL
y diagnosticar problemas de conectividad
"""

import asyncio
import asyncpg
import os
from pathlib import Path

# Configuración de BD desde .env
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ges_neu_bd',
    'user': 'postgres',
    'password': 'B3ll1c0s'
}

async def test_db_connection():
    """Prueba la conexión a PostgreSQL"""
    print("🔍 VERIFICANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Intentar conexión
        print(f"📡 Conectando a: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"📊 Base de datos: {DB_CONFIG['database']}")
        print(f"👤 Usuario: {DB_CONFIG['user']}")
        
        conn = await asyncpg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        print("✅ Conexión exitosa a PostgreSQL")
        
        # Verificar versión
        version = await conn.fetchval('SELECT version()')
        print(f"📋 Versión: {version}")
        
        # Verificar si la BD existe y tiene tablas
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        if len(tables) > 0:
            print("✅ Base de datos contiene tablas:")
            for i, table in enumerate(tables[:10]):  # Mostrar primeras 10
                print(f"   {i+1}. {table['table_name']}")
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
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table)
            
            status = "✅" if exists else "❌"
            print(f"{status} {table}")
        
        await conn.close()
        return True
        
    except asyncpg.InvalidCatalogNameError:
        print("❌ Error: Base de datos 'ges_neu_bd' no existe")
        print("💡 Solución: Crear la base de datos o verificar el nombre")
        return False
        
    except asyncpg.InvalidPasswordError:
        print("❌ Error: Credenciales incorrectas")
        print("💡 Solución: Verificar usuario/contraseña en .env")
        return False
        
    except ConnectionRefusedError:
        print("❌ Error: No se puede conectar a PostgreSQL")
        print("💡 Solución: Verificar que PostgreSQL esté ejecutándose")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        print(f"💡 Tipo de error: {type(e).__name__}")
        return False

def check_env_file():
    """Verifica si existe archivo .env"""
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    print("\n🔍 VERIFICANDO CONFIGURACIÓN:")
    
    if env_path.exists():
        print("✅ Archivo .env encontrado")
    else:
        print("❌ Archivo .env no encontrado")
        if env_example_path.exists():
            print("💡 Solución: Copiar .env.example a .env y configurar")
        
    if env_example_path.exists():
        print("✅ Archivo .env.example disponible como referencia")

async def main():
    print("🚀 DIAGNÓSTICO DE BASE DE DATOS - API GESNEU")
    print("=" * 60)
    
    # Verificar archivos de configuración
    check_env_file()
    
    # Probar conexión
    connection_ok = await test_db_connection()
    
    print("\n" + "=" * 60)
    if connection_ok:
        print("🎯 DIAGNÓSTICO COMPLETADO - CONEXIÓN OK")
        print("💡 La base de datos está disponible y contiene datos")
    else:
        print("🚨 DIAGNÓSTICO COMPLETADO - PROBLEMAS DETECTADOS")
        print("💡 Revisar configuración de PostgreSQL y credenciales")

if __name__ == "__main__":
    asyncio.run(main())
