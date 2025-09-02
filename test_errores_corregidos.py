#!/usr/bin/env python3
"""
Script para probar los 4 endpoints que tenían errores después de las correcciones.
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTMxNTYwMH0.YhQGhqtOJBZhvYvLEQs6wGQJ8YzQfpSQkOLKfVnuWJc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(url, method="GET", data=None, description=""):
    """Probar un endpoint específico."""
    try:
        print(f"\n🔍 Probando: {description}")
        print(f"   URL: {url}")
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                if isinstance(json_data, list):
                    print(f"   ✅ Respuesta: Lista con {len(json_data)} elementos")
                elif isinstance(json_data, dict):
                    print(f"   ✅ Respuesta: Objeto JSON con {len(json_data)} campos")
                else:
                    print(f"   ✅ Respuesta: {type(json_data)}")
            except:
                print(f"   ✅ Respuesta: {len(response.text)} caracteres")
        else:
            try:
                error_data = response.json()
                print(f"   ❌ Error: {error_data}")
            except:
                print(f"   ❌ Error: {response.text[:200]}...")
                
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Excepción: {str(e)}")
        return False

def main():
    print("🚀 === PRUEBA DE CORRECCIONES API GESNEU ===")
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    tests = [
        {
            "url": f"{BASE_URL}/api/v1/inventario/parametros",
            "description": "Inventario - Parámetros (Error 500 corregido)"
        },
        {
            "url": f"{BASE_URL}/api/v1/eventos/",
            "description": "Eventos - Lista (Error 404 corregido)"
        },
        {
            "url": f"{BASE_URL}/api/v1/garantias/vigentes",
            "description": "Garantías - Vigentes (Error 422 a revisar)"
        },
        {
            "url": f"{BASE_URL}/api/v1/alertas/",
            "description": "Alertas - Lista (Error 500 a revisar)"
        }
    ]
    
    resultados = []
    
    for test in tests:
        success = test_endpoint(test["url"], description=test["description"])
        resultados.append(success)
    
    print(f"\n📊 === RESUMEN ===")
    print(f"✅ Endpoints funcionando: {sum(resultados)}/4")
    print(f"❌ Endpoints con errores: {4 - sum(resultados)}/4")
    
    if sum(resultados) == 4:
        print("🎉 ¡Todos los errores han sido corregidos!")
    else:
        print("⚠️  Aún hay endpoints que requieren corrección")

if __name__ == "__main__":
    main()
