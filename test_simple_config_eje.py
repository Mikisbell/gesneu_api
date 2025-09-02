#!/usr/bin/env python3
"""
Test simple para diagnosticar error 500 en configuraciones-eje
"""
import requests
import json

def test_configuraciones_eje():
    """Test HTTP directo al endpoint problemático"""
    print("=== TEST CONFIGURACIONES-EJE ===")
    
    url = "http://localhost:8000/api/v1/vehiculos/configuraciones-eje"
    
    try:
        print(f"Realizando GET a: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("❌ ERROR 500 CONFIRMADO")
            try:
                error_detail = response.json()
                print(f"Detalle del error JSON:")
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print(f"Respuesta raw (no JSON):")
                print(response.text)
        elif response.status_code == 200:
            print("✅ ÉXITO - Endpoint funcionando")
            data = response.json()
            print(f"Registros obtenidos: {len(data)}")
            if data:
                print(f"Primer registro: {data[0]}")
        else:
            print(f"⚠ Status inesperado: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("¿Está el servidor corriendo en localhost:8000?")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_configuraciones_eje()
