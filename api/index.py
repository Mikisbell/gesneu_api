"""
App ultra-mínima para Vercel - Solo FastAPI básico
"""
import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Ultra minimal working"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"test": "working", "framework": "fastapi"}

@app.get("/env-test")
def env_test():
    return {
        "has_database_url": bool(os.getenv("DATABASE_URL")),
        "has_app_secret": bool(os.getenv("APP_SECRET_KEY")),
        "has_jwt_secret": bool(os.getenv("JWT_SECRET_KEY")),
        "app_env": os.getenv("APP_ENV", "NOT_SET"),
        "total_env_vars": len(os.environ)
    }

@app.get("/db-test")
def db_test():
    """Test de conexión a Supabase"""
    try:
        import asyncpg
        import asyncio
        
        async def test_connection():
            try:
                db_url = os.getenv("DATABASE_URL")
                if not db_url:
                    return {"error": "DATABASE_URL not found"}
                
                # Intentar conexión simple
                conn = await asyncpg.connect(db_url)
                result = await conn.fetchval("SELECT 1")
                await conn.close()
                
                return {"status": "success", "result": result, "connection": "ok"}
            except Exception as e:
                return {"error": str(e), "type": type(e).__name__}
        
        # Ejecutar test async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_connection())
        loop.close()
        
        return result
        
    except ImportError:
        return {"error": "asyncpg not available", "has_database_url": bool(os.getenv("DATABASE_URL"))}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}
