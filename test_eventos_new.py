import requests
import json

# Usar token proporcionado por el usuario
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njg1NDQ2MX0.F0eZfWMG-BWpZ3aX7Whlnc1hbdXsSghorVSWjd4_SVA"

print(f"✅ Usando token proporcionado: {token[:20]}...")

# Probar endpoint eventos
try:
    eventos_response = requests.get('http://localhost:8000/api/v1/eventos/', 
                                   headers={'Authorization': f'Bearer {token}'},
                                   timeout=10)
    
    print(f"Status eventos: {eventos_response.status_code}")
    
    if eventos_response.status_code == 200:
        data = eventos_response.json()
        print(f"✅ Eventos endpoint funcionando - {len(data)} eventos encontrados")
        if data:
            print(f"Primer evento: {json.dumps(data[0], indent=2, default=str)}")
        else:
            print("Lista de eventos vacía (normal si no hay datos)")
    else:
        print(f"❌ Error en eventos: {eventos_response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
