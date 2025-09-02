#!/usr/bin/env python3
"""
Script para probar el endpoint de proveedores después de corregir la dependencia get_session
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8001"
ENDPOINT = "/api/v1/catalogos/proveedores"

# Token JWT válido (actualizado)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NjgyNDgxOX0.1fmAvKbMorKg1sLxskLSzlspBxakPO0Y87szZVqOo8o"

async def test_endpoint():
    """Prueba el endpoint de proveedores"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Probando endpoint: {BASE_URL}{ENDPOINT}")
    print(f"⏰ Timestamp: {datetime.now()}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}{ENDPOINT}", headers=headers) as response:
                print(f"📊 Status Code: {response.status}")
                print(f"📋 Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Respuesta exitosa:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    text = await response.text()
                    print(f"❌ Error {response.status}:")
                    print(text)
                    
    except Exception as e:
        print(f"💥 Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
