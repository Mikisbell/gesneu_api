#!/usr/bin/env python3
"""
Script para probar múltiples endpoints de la API después de las correcciones
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8001"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NjgyNDgxOX0.1fmAvKbMorKg1sLxskLSzlspBxakPO0Y87szZVqOo8o"

# Endpoints a probar
ENDPOINTS = [
    "/api/v1/catalogos/proveedores",
    "/api/v1/catalogos/almacenes", 
    "/api/v1/catalogos/motivos-desecho",
    "/api/v1/catalogos/parametros-inventario",
    "/api/v1/vehiculos/",
    "/api/v1/neumaticos/fabricantes",
    "/api/v1/neumaticos/modelos",
    "/api/v1/inventario/neumaticos",
    "/api/v1/eventos/neumaticos",
    "/api/v1/garantias/neumaticos",
    "/api/v1/alertas/",
    "/docs",  # Swagger docs
    "/health"  # Health check
]

async def test_endpoint(session, endpoint):
    """Prueba un endpoint específico"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Probando: {endpoint}")
    
    try:
        async with session.get(url, headers=headers) as response:
            status = response.status
            
            if status == 200:
                print(f"✅ {endpoint} - Status: {status}")
                if endpoint.endswith("/docs"):
                    print("   📚 Swagger docs accesible")
                elif endpoint.endswith("/health"):
                    text = await response.text()
                    print(f"   💓 Health: {text}")
                else:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   📊 Retorna {len(data)} elementos")
                    else:
                        print(f"   📋 Respuesta: {type(data)}")
            else:
                text = await response.text()
                print(f"❌ {endpoint} - Status: {status}")
                print(f"   Error: {text[:200]}...")
                
    except Exception as e:
        print(f"💥 {endpoint} - Error de conexión: {e}")

async def run_tests():
    """Ejecuta todas las pruebas"""
    print(f"🚀 Iniciando pruebas de endpoints")
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    async with aiohttp.ClientSession() as session:
        # Probar endpoints en paralelo
        tasks = [test_endpoint(session, endpoint) for endpoint in ENDPOINTS]
        await asyncio.gather(*tasks)
    
    print(f"\n✅ Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(run_tests())
