"""
Servidor de prueba simple sin conexión a BD
"""
import os
os.environ['SKIP_DB_INIT'] = '1'

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Crear app simple para pruebas
app = FastAPI(
    title="GesNeu API Test",
    description="API de prueba sin BD",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "GesNeu API funcionando", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "skipped"}

@app.get("/test")
async def test():
    return {"test": "passed", "models": "working"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de prueba simple...")
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")
