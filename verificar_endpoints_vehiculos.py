#!/usr/bin/env python3
"""
Verificación rápida de todos los endpoints de vehículos después de corrección del enum
"""
import requests
import json

def test_vehiculos_endpoints():
    """Test de todos los endpoints de vehículos"""
    base_url = "http://localhost:8000/api/v1/vehiculos"
    
    endpoints = [
        "/tipos",
        "/configuraciones-eje", 
        "/posiciones-neumatico",
        "/"
    ]
    
    print("=== VERIFICACIÓN ENDPOINTS VEHÍCULOS ===")
    
    results = {}
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\n🔍 Probando: {endpoint}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"   ✅ Status 200 - {count} registros")
                results[endpoint] = "✅ OK"
            else:
                print(f"   ❌ Status {response.status_code}")
                if response.status_code == 500:
                    print(f"   📋 Error: {response.text}")
                results[endpoint] = f"❌ {response.status_code}"
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[endpoint] = f"❌ {type(e).__name__}"
    
    print("\n=== RESUMEN ===")
    for endpoint, status in results.items():
        print(f"{endpoint}: {status}")
    
    # Verificar si todos funcionan
    all_ok = all("✅" in status for status in results.values())
    if all_ok:
        print("\n🎉 ¡TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE!")
    else:
        failed = [ep for ep, st in results.items() if "❌" in st]
        print(f"\n⚠ Endpoints con problemas: {failed}")

if __name__ == "__main__":
    test_vehiculos_endpoints()
