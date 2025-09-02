#!/usr/bin/env python3
"""
Script para debuggear el error 500 en configuraciones-eje
"""
import requests
import json

BASE_URL = "http://localhost:8000"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NjgyNDgxOX0.1fmAvKbMorKg1sLxskLSzlspBxakPO0Y87szZVqOo8o"
headers = {'Authorization': f'Bearer {JWT_TOKEN}'}

def test_endpoint_debug(endpoint):
    """Prueba un endpoint con debug detallado"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"🔍 Probando: {url}")
        
        response = requests.get(url, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS: {len(data)} elementos")
                if data:
                    print(f"🔍 Primer elemento: {json.dumps(data[0], indent=2, default=str)}")
            except Exception as e:
                print(f"❌ Error parsing JSON: {e}")
                print(f"📄 Raw response: {response.text}")
        else:
            print(f"❌ ERROR {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    print("🚀 Debug de configuraciones-eje")
    test_endpoint_debug("/api/v1/vehiculos/configuraciones-eje")
