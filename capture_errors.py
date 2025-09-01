"""
Script para capturar errores detallados del servidor uvicorn
"""
import asyncio
import logging
import sys
from datetime import datetime

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_errors.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

async def test_auth_endpoint():
    """Test directo del endpoint de autenticación con captura de errores."""
    try:
        import httpx
        
        print(f"=== INICIANDO TEST DE AUTENTICACIÓN - {datetime.now()} ===")
        
        # Test del endpoint de autenticación
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/api/v1/auth/token",
                data={
                    "grant_type": "password",
                    "username": "admin",
                    "password": "Admin123",
                    "scope": "",
                    "client_id": "",
                    "client_secret": ""
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                print(f"❌ ERROR {response.status_code}: {response.text}")
            else:
                print("✅ Autenticación exitosa")
                
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Ejecuta este script DESPUÉS de iniciar uvicorn")
    print("Comando: uvicorn ges_neu_api.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug")
    print("\nPresiona Enter para continuar con el test...")
    input()
    
    asyncio.run(test_auth_endpoint())
