#!/usr/bin/env python3
"""
Test simple para verificar rutas de vehículos
"""
import requests

def test_vehiculos():
    base_url = "http://localhost:8001/api/v1/vehiculos"
    
    # Test 1: Lista de vehículos (funciona)
    print("1. Probando /vehiculos/")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ OK")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Test 2: Tipos de vehículo (problema)
    print("\n2. Probando /vehiculos/tipos")
    try:
        response = requests.get(f"{base_url}/tipos")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ OK")
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

if __name__ == "__main__":
    test_vehiculos()
