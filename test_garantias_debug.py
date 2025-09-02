#!/usr/bin/env python3
"""
Script para diagnosticar específicamente el error 422 en garantías
"""
import requests
import json

# Nuevo token válido
BASE_URL = "http://localhost:8000"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njg1NjU2MH0.TD-1nLWg6AWXFGtvPdUKBw-7uazqM_ET7nKX-aABHYk"
headers = {'Authorization': f'Bearer {JWT_TOKEN}'}

print("🔍 === DIAGNÓSTICO GARANTÍAS ===")

# Test 1: Verificar auth funciona
print("\n1. Verificando autenticación:")
try:
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"   Auth Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"   Usuario: {user_data.get('username', 'N/A')}")
    else:
        print(f"   Error: {response.text[:100]}")
except Exception as e:
    print(f"   Error conexión: {e}")

# Test 2: Verificar eventos funciona
print("\n2. Verificando eventos:")
try:
    response = requests.get(f"{BASE_URL}/api/v1/eventos/", headers=headers)
    print(f"   Eventos Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Eventos encontrados: {len(data)}")
    else:
        print(f"   Error: {response.text[:100]}")
except Exception as e:
    print(f"   Error conexión: {e}")

# Test 3: Diagnosticar garantías detalladamente
print("\n3. Diagnosticando garantías:")
try:
    response = requests.get(f"{BASE_URL}/api/v1/garantias/neumaticos", headers=headers)
    print(f"   Garantías Status: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    print(f"   Response Text: {response.text[:500]}")
    
    if response.status_code == 422:
        try:
            error_detail = response.json()
            print(f"   Error Detail: {json.dumps(error_detail, indent=2)}")
        except:
            print("   No se pudo parsear JSON del error")
            
except Exception as e:
    print(f"   Error conexión: {e}")

# Test 4: Verificar documentación de garantías
print("\n4. Verificando documentación OpenAPI:")
try:
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi_data = response.json()
        garantias_paths = {k: v for k, v in openapi_data.get("paths", {}).items() if "garantias" in k}
        print(f"   Endpoints garantías en OpenAPI: {len(garantias_paths)}")
        for path in garantias_paths.keys():
            print(f"     - {path}")
    else:
        print(f"   Error OpenAPI: {response.status_code}")
except Exception as e:
    print(f"   Error OpenAPI: {e}")

print("\n✅ Diagnóstico completado")
