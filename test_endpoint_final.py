import requests
import json

# Test endpoint with proper error handling
url = "http://127.0.0.1:8001/api/v1/catalogos/proveedores"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ ÉXITO - Endpoint funcionando correctamente")
        data = response.json()
        print(f"📊 Datos recibidos: {len(data)} proveedores")
        if data:
            print(f"📄 Primer proveedor: {json.dumps(data[0], indent=2, default=str)}")
    else:
        print(f"❌ ERROR {response.status_code}")
        print(f"🔥 Respuesta: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"💥 Error de conexión: {e}")
except Exception as e:
    print(f"⚠️ Error general: {e}")
