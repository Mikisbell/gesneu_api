#!/usr/bin/env python3
"""
Test simple para diagnosticar error 500 en módulo Eventos.
"""
import requests

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTMxNTYwMH0.YhQGhqtOJBZhvYvLEQs6wGQJ8YzQfpSQkOLKfVnuWJc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_eventos():
    """Probar endpoint de eventos con manejo de errores detallado."""
    try:
        print("🔍 Probando endpoint /api/v1/eventos/")
        
        response = requests.get(f"{BASE_URL}/api/v1/eventos/", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("❌ Error 500 - Contenido de respuesta:")
            print(response.text)
        elif response.status_code == 200:
            print("✅ Respuesta exitosa:")
            print(response.json())
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")

if __name__ == "__main__":
    test_eventos()
