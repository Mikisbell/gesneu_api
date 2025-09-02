#!/usr/bin/env python3
"""
Test script for catalog endpoints after model corrections
"""
import urllib.request
import urllib.parse
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8001"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2"

def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib"""
    if headers is None:
        headers = {}
    
    headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    headers["Content-Type"] = "application/json"
    
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            return status_code, response_data
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def test_endpoint(name, url, method="GET", data=None):
    """Test a single endpoint"""
    print(f"\n🔍 Testing {name}: {method} {url}")
    status, response = make_request(url, method, data)
    
    if status:
        if status == 200:
            print(f"✅ SUCCESS: {status}")
            try:
                json_response = json.loads(response)
                if isinstance(json_response, list):
                    print(f"   📊 Returned {len(json_response)} items")
                elif isinstance(json_response, dict):
                    print(f"   📋 Response keys: {list(json_response.keys())}")
            except:
                print(f"   📄 Response length: {len(response)} chars")
        else:
            print(f"❌ ERROR: {status}")
            print(f"   📄 Response: {response[:200]}...")
    else:
        print(f"💥 CONNECTION ERROR: {response}")

def main():
    print("🚀 Testing GesNeu API Catalog Endpoints")
    print("=" * 50)
    
    # Test basic connectivity
    test_endpoint("API Health", f"{BASE_URL}/")
    test_endpoint("API Docs", f"{BASE_URL}/docs")
    
    # Test catalog endpoints
    catalog_endpoints = [
        ("Proveedores List", f"{BASE_URL}/api/v1/catalogos/proveedores"),
        ("Almacenes List", f"{BASE_URL}/api/v1/catalogos/almacenes"),
        ("Motivos Desecho List", f"{BASE_URL}/api/v1/catalogos/motivos-desecho"),
        ("Parametros Inventario List", f"{BASE_URL}/api/v1/catalogos/parametros-inventario"),
    ]
    
    print("\n📦 CATALOG ENDPOINTS:")
    print("-" * 30)
    
    for name, url in catalog_endpoints:
        test_endpoint(name, url)
    
    # Test auth endpoint
    print("\n🔐 AUTH ENDPOINTS:")
    print("-" * 20)
    test_endpoint("Auth Token", f"{BASE_URL}/api/v1/auth/token", "POST", {
        "username": "admin",
        "password": "Admin123"
    })
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()
