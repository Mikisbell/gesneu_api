#!/usr/bin/env python3
"""
Test de endpoints con rutas corregidas según los routers actualizados.
"""
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTMxNTYwMH0.YhQGhqtOJBZhvYvLEQs6wGQJ8YzQfpSQkOLKfVnuWJc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(endpoint, description):
    """Probar un endpoint específico."""
    try:
        print(f"\n🔍 Probando {description}: {endpoint}")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Exitoso - {len(data)} elementos")
        else:
            print(f"❌ Error - Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")

def main():
    """Probar todos los endpoints con rutas corregidas."""
    print("🚀 Probando endpoints con rutas corregidas...")
    
    # Rutas correctas según los routers actualizados
    endpoints = [
        ("/api/v1/inventario/neumaticos", "Inventario Neumáticos"),
        ("/api/v1/eventos/", "Eventos (GET)"),  # Ruta corregida
        ("/api/v1/garantias/", "Garantías (GET)"),  # Ruta corregida  
        ("/api/v1/alertas/", "Alertas"),
    ]
    
    for endpoint, description in endpoints:
        test_endpoint(endpoint, description)
    
    print("\n📊 Resumen de pruebas completado")

if __name__ == "__main__":
    main()
