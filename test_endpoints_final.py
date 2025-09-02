#!/usr/bin/env python3
"""
Prueba final de endpoints corregidos
"""
import requests
import json

def test_endpoint(url, name):
    """Prueba un endpoint específico"""
    try:
        print(f"Probando {name}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            try:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"✅ {name}: Status 200 - {count} elementos")
                return True
            except:
                print(f"✅ {name}: Status 200 - Respuesta OK")
                return True
        else:
            print(f"❌ {name}: Status {response.status_code}")
            print(f"   Error: {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: No se puede conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    """Ejecutar pruebas de endpoints"""
    base_url = "http://localhost:8001/api/v1"
    
    tests = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/inventario/parametros", "Parámetros Inventario (antes 404)"),
        (f"{base_url}/neumaticos/modelos", "Modelos Neumáticos (antes 500)"),
        (f"{base_url}/catalogos/proveedores", "Proveedores (control)"),
    ]
    
    print("PRUEBA DE ENDPOINTS CORREGIDOS")
    print("=" * 50)
    
    results = []
    for url, name in tests:
        success = test_endpoint(url, name)
        results.append((name, success))
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    for name, success in results:
        status = "✅ OK" if success else "❌ FALLO"
        print(f"  {status} {name}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\nResultado: {success_count}/{len(results)} endpoints funcionando")

if __name__ == "__main__":
    main()
