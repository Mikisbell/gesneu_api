"""
Test de conexión a la base de datos PostgreSQL
"""
import asyncio
import asyncpg
import os

async def test_database_connection():
    """Prueba la conexión a PostgreSQL"""
    try:
        # Usar la misma URL del .env
        db_url = "postgresql://postgres:B3ll1c0s@localhost:5432/ges_neu_bd"
        
        print("🔌 Probando conexión a PostgreSQL...")
        conn = await asyncpg.connect(db_url)
        
        # Probar una consulta simple
        result = await conn.fetchval("SELECT version()")
        print(f"✅ Conexión exitosa a PostgreSQL")
        print(f"📊 Versión: {result[:50]}...")
        
        # Verificar que la base de datos ges_neu_bd existe
        db_name = await conn.fetchval("SELECT current_database()")
        print(f"📁 Base de datos actual: {db_name}")
        
        # Contar tablas existentes
        table_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print(f"📋 Tablas en la BD: {table_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

async def test_specific_tables():
    """Verifica que las tablas principales existen"""
    try:
        db_url = "postgresql://postgres:B3ll1c0s@localhost:5432/ges_neu_bd"
        conn = await asyncpg.connect(db_url)
        
        # Tablas principales que deben existir
        expected_tables = [
            'usuarios', 'roles', 'permisos',
            'vehiculos', 'tipos_vehiculo',
            'neumaticos', 'fabricantes_neumatico', 'modelos_neumatico',
            'almacenes', 'proveedores'
        ]
        
        print("\n🔍 Verificando tablas principales:")
        for table in expected_tables:
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table)
            
            status = "✅" if exists else "❌"
            print(f"{status} {table}: {'Existe' if exists else 'No existe'}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")

if __name__ == "__main__":
    print("🚀 Probando conexión a base de datos GesNeu")
    print("=" * 60)
    
    # Probar conexión básica
    success = asyncio.run(test_database_connection())
    
    if success:
        # Si la conexión funciona, verificar tablas
        asyncio.run(test_specific_tables())
        
        print("\n" + "=" * 60)
        print("🎉 Conexión a base de datos verificada")
        print("✅ Lista para usar con la API")
    else:
        print("\n" + "=" * 60)
        print("❌ Problemas de conexión a la base de datos")
        print("🔧 Verifica que PostgreSQL esté ejecutándose")
        print("🔧 Verifica las credenciales en .env")
