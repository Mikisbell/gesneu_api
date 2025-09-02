#!/usr/bin/env python3
"""
Script para probar endpoints con detalles de errores
"""
import asyncio
import httpx
import json

async def test_fabricantes():
    """Prueba endpoint fabricantes con detalles de error"""
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc4MDM5MH0.mjWUaVDnmznHp_a4m2zfshDquv0XRuZFqR-FGReaDQE'
    headers = {'Authorization': f'Bearer {token}'}
    
    print("=== PROBANDO FABRICANTES ===")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://localhost:8000/api/v1/neumaticos/fabricantes', headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 422:
                print("Error 422 - Detalles:")
                try:
                    error_detail = response.json()
                    print(json.dumps(error_detail, indent=2))
                except:
                    print(response.text)
            elif response.status_code == 200:
                print("✅ Éxito!")
                data = response.json()
                print(f"Registros encontrados: {len(data)}")
            else:
                print(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Error de conexión: {e}")

async def test_vehiculos():
    """Prueba endpoint vehículos con detalles de error"""
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc4MDM5MH0.mjWUaVDnmznHp_a4m2zfshDquv0XRuZFqR-FGReaDQE'
    headers = {'Authorization': f'Bearer {token}'}
    
    print("\n=== PROBANDO VEHÍCULOS ===")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://localhost:8000/api/v1/vehiculos/', headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 500:
                print("Error 500 - Detalles:")
                print(response.text)
            elif response.status_code == 200:
                print("✅ Éxito!")
                data = response.json()
                print(f"Registros encontrados: {len(data)}")
            else:
                print(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Error de conexión: {e}")

async def main():
    await test_fabricantes()
    await test_vehiculos()

if __name__ == "__main__":
    asyncio.run(main())
