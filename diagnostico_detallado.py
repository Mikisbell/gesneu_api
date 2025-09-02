#!/usr/bin/env python3
"""
Diagnóstico detallado de errores 500 y 404 en endpoints críticos
"""
import requests
import json
import traceback

def test_endpoint_detailed(url, name):
    """Prueba un endpoint con detalles completos"""
    print(f"\n{'='*60}")
    print(f"PROBANDO: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ ÉXITO - Elementos: {len(data) if isinstance(data, list) else 'N/A'}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"Primer elemento: {json.dumps(data[0], indent=2, default=str)[:300]}...")
            except:
                print(f"✅ ÉXITO - Respuesta texto: {response.text[:200]}...")
        else:
            print(f"❌ ERROR {response.status_code}")
            print(f"Respuesta completa: {response.text}")
            
            # Intentar parsear como JSON para más detalles
            try:
                error_data = response.json()
                print(f"Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor. ¿Está corriendo en puerto 8001?")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Timeout - El servidor no responde")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")
        print(traceback.format_exc())

def main():
    """Ejecutar diagnóstico completo"""
    base_url = "http://localhost:8001/api/v1"
    
    endpoints = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/neumaticos/modelos", "Modelos Neumáticos (ERROR 500)"),
        (f"{base_url}/inventario/parametros", "Parámetros Inventario (ERROR 404)"),
        (f"{base_url}/catalogos/proveedores", "Proveedores (OK)"),
    ]
    
    print("DIAGNÓSTICO DETALLADO DE ENDPOINTS")
    print("=" * 80)
    
    for url, name in endpoints:
        test_endpoint_detailed(url, name)
    
    print(f"\n{'='*80}")
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()
