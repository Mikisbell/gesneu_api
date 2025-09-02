#!/usr/bin/env python3
"""
Script para probar directamente los endpoints de vehículos
y verificar si el problema de rutas está resuelto.
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1/vehiculos"

def test_endpoint(url, name):
    """Prueba un endpoint específico."""
    try:
        print(f"Probando {name}...")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: OK - {len(data) if isinstance(data, list) else 'objeto'} elementos")
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"❌ {name}: Error 422 - Validación")
            print(f"   Detalle: {json.dumps(error_detail, indent=2)}")
        else:
            print(f"❌ {name}: Status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detalle: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Texto: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Error de conexión - ¿Servidor corriendo?")
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
    
    print("-" * 60)

def main():
    """Función principal."""
    print("PRUEBA DIRECTA DE ENDPOINTS DE VEHÍCULOS")
    print("=" * 60)
    
    # Probar endpoints específicos
    test_endpoint(f"{BASE_URL}/", "Lista Vehículos")
    test_endpoint(f"{BASE_URL}/tipos", "Tipos Vehículo")
    test_endpoint(f"{BASE_URL}/configuraciones-eje", "Configuraciones Eje")
    test_endpoint(f"{BASE_URL}/posiciones-neumatico", "Posiciones Neumático")

if __name__ == "__main__":
    main()
