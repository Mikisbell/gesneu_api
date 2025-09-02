#!/usr/bin/env python3
"""
Test específico para diagnosticar error 500 en módulo inventario
"""
import requests
import json

def test_inventario_endpoint():
    """Test del endpoint de inventario que está fallando"""
    print("=== DIAGNÓSTICO INVENTARIO ERROR 500 ===")
    
    base_url = "http://localhost:8000/api/v1/inventario"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njg0NTkzOH0.nuIw2u_J4_tjbHD8icExadeUq6LA_lHNmC-xP-KVZNc"
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoints = [
        "/parametros",
        "/resumen", 
        "/neumaticos",
        "/stock-bajo"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\n🔍 Probando: {endpoint}")
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 500:
                print("   ❌ ERROR 500 - Internal Server Error")
                try:
                    error_data = response.json()
                    print(f"   📋 Error JSON: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   📋 Error raw: {response.text}")
            elif response.status_code == 200:
                print("   ✅ SUCCESS")
                try:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "N/A"
                    print(f"   📊 Registros: {count}")
                except:
                    print(f"   📊 Response: {response.text[:100]}...")
            else:
                print(f"   ⚠ Status inesperado: {response.status_code}")
                print(f"   📋 Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ ERROR: No se puede conectar al servidor")
        except Exception as e:
            print(f"   ❌ ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_inventario_endpoint()
