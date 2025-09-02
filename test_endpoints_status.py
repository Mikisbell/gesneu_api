#!/usr/bin/env python3
"""
Test script to check the status of critical API endpoints
"""
import requests
import json
import sys
from datetime import datetime

def test_endpoint(base_url, endpoint, description=""):
    """Test a single endpoint and return status"""
    try:
        url = f"{base_url}{endpoint}"
        print(f"Testing {endpoint} - {description}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"  ✅ Status: {response.status_code} - Items: {count}")
                return True
            except:
                print(f"  ✅ Status: {response.status_code} - Response OK")
                return True
        else:
            print(f"  ❌ Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"  Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  🔌 Connection failed - Server may not be running")
        return False
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def main():
    base_url = "http://localhost:8000/api/v1"
    
    print(f"🔍 Testing API Endpoints - {datetime.now()}")
    print("=" * 50)
    
    # Test health endpoint first
    health_ok = test_endpoint("http://localhost:8000", "/health", "Health Check")
    
    if not health_ok:
        print("\n❌ API Server is not responding. Please start the server first:")
        print("python -m uvicorn ges_neu_api.main:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    
    print("\n📋 Testing Critical Endpoints:")
    print("-" * 30)
    
    # Test the problematic endpoints
    endpoints = [
        ("/neumaticos/modelos", "Tire Models - Previously had 500 error"),
        ("/inventario/parametros", "Inventory Parameters - Previously had 500 error"),
        ("/catalogos/proveedores", "Suppliers - Should work"),
        ("/catalogos/almacenes", "Warehouses - Should work"),
        ("/catalogos/motivos-desecho", "Disposal Reasons - Should work"),
        ("/vehiculos/tipos", "Vehicle Types - May have 422 error"),
        ("/vehiculos/configuraciones-eje", "Axle Configurations - May have 422 error"),
        ("/vehiculos/posiciones-neumatico", "Tire Positions - May have 422 error"),
    ]
    
    results = []
    for endpoint, description in endpoints:
        success = test_endpoint(base_url, endpoint, description)
        results.append((endpoint, success))
    
    print("\n📊 Summary:")
    print("-" * 20)
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for endpoint, success in results:
        status = "✅ OK" if success else "❌ FAIL"
        print(f"  {status} {endpoint}")
    
    print(f"\n🎯 Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints still need fixes")

if __name__ == "__main__":
    main()
