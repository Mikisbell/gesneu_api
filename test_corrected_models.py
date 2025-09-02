#!/usr/bin/env python3
"""
Test script to verify corrected models work with API endpoints
Tests all major modules after schema alignment corrections
"""
import urllib.request
import urllib.error
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8001"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2"

def test_endpoint(name, url, method="GET", data=None):
    """Test a single endpoint and return status"""
    try:
        headers = {
            'Authorization': f'Bearer {JWT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        if data:
            data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            content = response.read().decode('utf-8')
            
            if status == 200:
                print(f"✅ {name}: SUCCESS ({status})")
                try:
                    json_data = json.loads(content)
                    if isinstance(json_data, list):
                        print(f"   📊 Returned {len(json_data)} items")
                    elif isinstance(json_data, dict):
                        print(f"   📋 Response keys: {list(json_data.keys())[:5]}")
                except:
                    print(f"   📄 Response length: {len(content)} chars")
            else:
                print(f"⚠️  {name}: {status}")
                
            return status, content
            
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8')
        print(f"❌ {name}: HTTP {e.code}")
        if e.code == 500:
            print(f"   🔥 SERVER ERROR: {error_content[:200]}")
        elif e.code == 401:
            print(f"   🔐 AUTH ERROR: {error_content[:100]}")
        elif e.code == 404:
            print(f"   🔍 NOT FOUND: {error_content[:100]}")
        return e.code, error_content
        
    except Exception as e:
        print(f"💥 {name}: CONNECTION ERROR - {str(e)}")
        return None, str(e)

def main():
    print("🚀 Testing GesNeu API - Corrected Models")
    print("=" * 50)
    
    # Test basic connectivity
    print("\n📡 BASIC CONNECTIVITY:")
    print("-" * 25)
    test_endpoint("API Root", f"{BASE_URL}/")
    test_endpoint("API Docs", f"{BASE_URL}/docs")
    
    # Test corrected catalog endpoints
    print("\n📦 CATALOG ENDPOINTS (CORRECTED):")
    print("-" * 35)
    catalog_endpoints = [
        ("Proveedores", f"{BASE_URL}/api/v1/catalogos/proveedores"),
        ("Almacenes", f"{BASE_URL}/api/v1/catalogos/almacenes"),
        ("Motivos Desecho", f"{BASE_URL}/api/v1/catalogos/motivos-desecho"),
        ("Parametros Inventario", f"{BASE_URL}/api/v1/catalogos/parametros-inventario"),
    ]
    
    for name, url in catalog_endpoints:
        test_endpoint(name, url)
    
    # Test neumaticos endpoints
    print("\n🛞 NEUMATICOS ENDPOINTS (CORRECTED):")
    print("-" * 35)
    neumaticos_endpoints = [
        ("Fabricantes", f"{BASE_URL}/api/v1/neumaticos/fabricantes"),
        ("Modelos", f"{BASE_URL}/api/v1/neumaticos/modelos"),
        ("Neumaticos", f"{BASE_URL}/api/v1/neumaticos/neumaticos"),
    ]
    
    for name, url in neumaticos_endpoints:
        test_endpoint(name, url)
    
    # Test vehiculos endpoints
    print("\n🚛 VEHICULOS ENDPOINTS (VERIFIED):")
    print("-" * 35)
    vehiculos_endpoints = [
        ("Tipos Vehiculo", f"{BASE_URL}/api/v1/vehiculos/tipos-vehiculo"),
        ("Vehiculos", f"{BASE_URL}/api/v1/vehiculos/vehiculos"),
        ("Configuraciones Eje", f"{BASE_URL}/api/v1/vehiculos/configuraciones-eje"),
        ("Posiciones Neumatico", f"{BASE_URL}/api/v1/vehiculos/posiciones-neumatico"),
    ]
    
    for name, url in vehiculos_endpoints:
        test_endpoint(name, url)
    
    # Test other modules
    print("\n🔧 OTHER MODULES:")
    print("-" * 20)
    other_endpoints = [
        ("Auth Token", f"{BASE_URL}/api/v1/auth/token", "POST", {
            "username": "admin", 
            "password": "Admin123"
        }),
        ("Inventario", f"{BASE_URL}/api/v1/inventario/inventario-neumaticos"),
        ("Eventos", f"{BASE_URL}/api/v1/eventos/eventos-neumaticos"),
        ("Garantias", f"{BASE_URL}/api/v1/garantias/garantias-neumaticos"),
        ("Alertas", f"{BASE_URL}/api/v1/alertas/alertas"),
    ]
    
    for item in other_endpoints:
        if len(item) == 4:
            name, url, method, data = item
            test_endpoint(name, url, method, data)
        else:
            name, url = item
            test_endpoint(name, url)
    
    print("\n" + "=" * 50)
    print("✅ Model alignment test completed!")
    print("🎯 Focus: Catalog, Neumaticos, and Vehiculos models corrected")

if __name__ == "__main__":
    main()
