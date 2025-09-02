#!/usr/bin/env python3
"""
Script para probar los endpoints de vehículos reconstruidos - VERSIÓN ACTUALIZADA
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1/vehiculos"

def test_endpoint(url: str, method: str = "GET", data: Dict[Any, Any] = None) -> None:
    """Prueba un endpoint y muestra el resultado"""
    try:
        print(f"\n🔍 Probando {method} {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Método {method} no soportado")
            return
            
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS - ENDPOINT FUNCIONANDO CORRECTAMENTE")
            try:
                json_response = response.json()
                if isinstance(json_response, list):
                    print(f"📋 Elementos encontrados: {len(json_response)}")
                    if json_response:
                        print(f"🔍 Primer elemento: {json.dumps(json_response[0], indent=2, default=str)}")
                    else:
                        print("📋 Lista vacía (sin datos en BD)")
                else:
                    print(f"📄 Respuesta: {json.dumps(json_response, indent=2, default=str)}")
            except json.JSONDecodeError:
                print(f"📄 Respuesta (texto): {response.text}")
        elif response.status_code == 422:
            print("❌ ERROR 422 - VALIDATION ERROR (PROBLEMA ANTERIOR)")
            print(f"📄 Detalles: {response.text}")
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - ¿Está el servidor corriendo en localhost:8000?")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def main():
    """Función principal para probar todos los endpoints"""
    print("🚀 Iniciando pruebas de endpoints de vehículos RECONSTRUIDOS...")
    print("📋 Probando endpoints que anteriormente causaban ERROR 422")
    
    # Endpoints que anteriormente causaban error 422
    endpoints_to_test = [
        f"{BASE_URL}/tipos",
        f"{BASE_URL}/configuraciones-eje", 
        f"{BASE_URL}/posiciones-neumatico",
        f"{BASE_URL}/",  # Lista de vehículos
    ]
    
    for endpoint in endpoints_to_test:
        test_endpoint(endpoint)
    
    # Probar también la documentación
    print(f"\n🔍 Probando documentación Swagger...")
    test_endpoint("http://localhost:8000/docs")
    
    print("\n🏁 Pruebas completadas")
    print("✅ Si todos los endpoints muestran Status 200, la reconstrucción fue exitosa")

if __name__ == "__main__":
    main()
