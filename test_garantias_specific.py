#!/usr/bin/env python3
"""
Test específico para diagnosticar error 422 en garantías
"""
import requests
import json

BASE_URL = "http://localhost:8000"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njg1NjU2MH0.TD-1nLWg6AWXFGtvPdUKBw-7uazqM_ET7nKX-aABHYk"
headers = {'Authorization': f'Bearer {JWT_TOKEN}'}

print("🔍 DIAGNÓSTICO ESPECÍFICO - GARANTÍAS")

# Test del endpoint exacto que falla
endpoint = "/api/v1/garantias/neumaticos"
print(f"\n📋 Testing: {endpoint}")

try:
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if response.status_code == 422:
        print("\n❌ ERROR 422 - DETALLES:")
        try:
            error_detail = response.json()
            print(json.dumps(error_detail, indent=2, ensure_ascii=False))
        except:
            print("Raw response text:")
            print(response.text)
    elif response.status_code == 200:
        print("✅ SUCCESS - Response OK")
        data = response.json()
        print(f"Data count: {len(data) if isinstance(data, list) else 'Not a list'}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"💥 Connection error: {e}")

# Verificar si el endpoint existe en OpenAPI
print(f"\n📖 Verificando OpenAPI...")
try:
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get("paths", {})
        
        # Buscar endpoints de garantías
        garantias_endpoints = []
        for path in paths.keys():
            if "garantias" in path:
                garantias_endpoints.append(path)
        
        print(f"Endpoints garantías encontrados: {len(garantias_endpoints)}")
        for ep in garantias_endpoints:
            print(f"  - {ep}")
            
        # Verificar si nuestro endpoint específico existe
        if endpoint in paths:
            print(f"\n✅ Endpoint {endpoint} existe en OpenAPI")
            methods = list(paths[endpoint].keys())
            print(f"Métodos disponibles: {methods}")
        else:
            print(f"\n❌ Endpoint {endpoint} NO existe en OpenAPI")
            print("Endpoints similares:")
            for ep in garantias_endpoints:
                print(f"  - {ep}")
    else:
        print(f"Error obteniendo OpenAPI: {response.status_code}")
except Exception as e:
    print(f"Error OpenAPI: {e}")

print(f"\n✅ Diagnóstico completado")
