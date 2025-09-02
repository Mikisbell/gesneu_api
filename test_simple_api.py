#!/usr/bin/env python3
"""
Simple API test using only standard library
"""
import urllib.request
import urllib.error
import json

def test_endpoint(url, token):
    """Test a single endpoint"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            content = response.read().decode('utf-8')
            return status, content
            
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

# Test configuration
BASE_URL = "http://127.0.0.1:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2"

print("🚀 Testing GesNeu API")
print("=" * 40)

# Test endpoints
endpoints = [
    ("API Root", f"{BASE_URL}/"),
    ("Proveedores", f"{BASE_URL}/api/v1/catalogos/proveedores"),
    ("Almacenes", f"{BASE_URL}/api/v1/catalogos/almacenes"),
    ("Motivos Desecho", f"{BASE_URL}/api/v1/catalogos/motivos-desecho"),
]

for name, url in endpoints:
    print(f"\n🔍 Testing {name}:")
    status, response = test_endpoint(url, TOKEN)
    
    if status == 200:
        print(f"✅ SUCCESS: {status}")
        try:
            data = json.loads(response)
            if isinstance(data, list):
                print(f"   📊 Items: {len(data)}")
            else:
                print(f"   📋 Type: {type(data).__name__}")
        except:
            print(f"   📄 Length: {len(response)} chars")
    elif status:
        print(f"❌ ERROR: {status}")
        print(f"   📄 Response: {response[:200]}")
    else:
        print(f"💥 CONNECTION ERROR: {response}")

print("\n" + "=" * 40)
print("✅ Test completed!")
