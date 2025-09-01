"""
Test simple de conexión a BD PostgreSQL
"""
import asyncio
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_db_connection():
    """Prueba la conexión directa a PostgreSQL."""
    try:
        import asyncpg
        
        # Obtener configuración desde .env
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', 5432))
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        db_name = os.getenv('DB_NAME', 'ges_neu_bd')
        
        print(f"Intentando conectar a: {db_host}:{db_port}/{db_name} como {db_user}")
        
        # Crear conexión directa
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        # Ejecutar consulta simple
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Conexión exitosa: {result}")
        
        # Verificar si existe la tabla usuarios
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios'
            )
        """)
        print(f"✅ Tabla usuarios existe: {exists}")
        
        # Contar usuarios
        if exists:
            count = await conn.fetchval("SELECT COUNT(*) FROM usuarios")
            print(f"✅ Total usuarios: {count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_db_connection())
