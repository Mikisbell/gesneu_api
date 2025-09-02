#!/usr/bin/env python3
"""
Script para verificar el estado actual de los endpoints después de las correcciones
"""
import requests
import json

# Token JWT válido
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc4MDM5MH0.mjWUaVDnmznHp_a4m2zfshDquv0XRuZFqR-FGReaDQE"
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_endpoint(endpoint, name):
    """Prueba un endpoint y devuelve el status"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"✅ {name}: {response.status_code} - {count} elementos")
            except:
                print(f"✅ {name}: {response.status_code} - OK")
        else:
            print(f"❌ {name}: {response.status_code}")
            if response.status_code == 422:
                print(f"   Error 422: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Error de conexión - {e}")
    except Exception as e:
        print(f"❌ {name}: Error - {e}")

if __name__ == "__main__":
    print("=== ESTADO ACTUAL DE ENDPOINTS DESPUÉS DE CORRECCIONES ===\n")
    
    # Endpoints de neumáticos (corregidos)
    print("📦 NEUMÁTICOS:")
    test_endpoint("/neumaticos/", "Neumáticos")
    test_endpoint("/neumaticos/fabricantes", "Fabricantes")
    test_endpoint("/neumaticos/modelos", "Modelos")
    
    print("\n🚗 VEHÍCULOS:")
    test_endpoint("/vehiculos/", "Vehículos")
    test_endpoint("/vehiculos/tipos", "Tipos Vehículo")
    
    print("\n📋 CATÁLOGOS (ya funcionando):")
    test_endpoint("/catalogos/proveedores", "Proveedores")
    test_endpoint("/catalogos/almacenes", "Almacenes")
    
    print("\n🔐 AUTENTICACIÓN:")
    test_endpoint("/auth/me", "Usuario Actual")
    
    print("\n🏥 SALUD:")
    test_endpoint("/health", "Health Check")
