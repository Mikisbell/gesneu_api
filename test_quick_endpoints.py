#!/usr/bin/env python3
"""
Test rápido de endpoints específicos después de correcciones
"""
import urllib.request
import json

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc1MTExM30._N4mycyYTHbpI5s2tTozOTlIW0y2aI7vrYX7kwF40hg"

def test_endpoint(url, name):
    """Test específico de endpoint"""
    try:
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
            print(f"✅ {name}: {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ {name}: {e.code} - {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def main():
    print("🔍 PRUEBAS RÁPIDAS POST-CORRECCIÓN\n")
    
    # Endpoints corregidos
    endpoints = [
        (f"{BASE_URL}/api/v1/vehiculos/", "Vehículos"),
        (f"{BASE_URL}/api/v1/neumaticos/modelos", "Modelos neumáticos"),
        (f"{BASE_URL}/api/v1/bitacoras/operaciones", "Bitácoras operaciones"),
        (f"{BASE_URL}/api/v1/sistema/rutas", "Sistema rutas"),
        (f"{BASE_URL}/api/v1/sistema/tipos-ruta", "Sistema tipos-ruta")
    ]
    
    results = []
    for url, name in endpoints:
        result = test_endpoint(url, name)
        results.append((name, result))
    
    print(f"\n📊 RESULTADOS:")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n🎯 {success_count}/{len(results)} endpoints corregidos")

if __name__ == "__main__":
    main()
