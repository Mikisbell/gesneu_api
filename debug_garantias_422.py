#!/usr/bin/env python3
"""
Diagnóstico específico del error 422 en garantías
"""
import requests
import json

BASE_URL = "http://localhost:8000"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njg1NjU2MH0.TD-1nLWg6AWXFGtvPdUKBw-7uazqM_ET7nKX-aABHYk"
headers = {'Authorization': f'Bearer {JWT_TOKEN}'}

print("🔍 DIAGNÓSTICO DETALLADO - GARANTÍAS 422")

# Test específico del endpoint que falla
try:
    response = requests.get(f"{BASE_URL}/api/v1/garantias/neumaticos", headers=headers)
    print(f"\n📋 Endpoint: /api/v1/garantias/neumaticos")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 422:
        print(f"\n❌ Error 422 - Detalles:")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print("No se pudo parsear JSON")
            print(f"Raw response: {response.text}")
    else:
        print(f"Response: {response.text[:300]}")
        
except Exception as e:
    print(f"💥 Error: {e}")

# Verificar documentación OpenAPI para garantías
try:
    print(f"\n📖 Verificando OpenAPI...")
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get("paths", {})
        garantias_paths = {k: v for k, v in paths.items() if "garantias" in k}
        print(f"Endpoints garantías en OpenAPI: {len(garantias_paths)}")
        for path, methods in garantias_paths.items():
            print(f"  {path}: {list(methods.keys())}")
    else:
        print(f"Error OpenAPI: {response.status_code}")
except Exception as e:
    print(f"Error OpenAPI: {e}")

print(f"\n✅ Diagnóstico completado")
