#!/usr/bin/env python3
"""
Direct endpoint testing using requests
"""
import requests
import json

def test_endpoint(url, name):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=10)
        print(f"{name}: Status {response.status_code}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"  Error detail: {error_data.get('detail', 'No detail')}")
            except:
                print(f"  Raw error: {response.text[:200]}")
        else:
            try:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"  Success: {count} items")
            except:
                print(f"  Success: Response OK")
                
    except requests.exceptions.ConnectionError:
        print(f"{name}: Connection failed - server not running")
    except Exception as e:
        print(f"{name}: Error - {str(e)}")

if __name__ == "__main__":
    base_url = "http://localhost:8001"
    
    print("Testing API endpoints...")
    test_endpoint(f"{base_url}/health", "Health Check")
    test_endpoint(f"{base_url}/api/v1/neumaticos/modelos", "Tire Models")
    test_endpoint(f"{base_url}/api/v1/inventario/parametros", "Inventory Parameters")
    test_endpoint(f"{base_url}/api/v1/catalogos/proveedores", "Suppliers")
