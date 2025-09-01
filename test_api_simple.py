"""
Test simple de la API GesNeu usando urllib (sin dependencias externas)
"""
import urllib.request
import urllib.error
import json
import time

def test_endpoint(url, description):
    """Prueba un endpoint específico"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            print(f"✅ {description}: HTTP {status_code}")
            return True, status_code, content
    except urllib.error.HTTPError as e:
        print(f"⚠️  {description}: HTTP {e.code}")
        return False, e.code, str(e)
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False, 0, str(e)

def main():
    base_url = "http://localhost:8001"
    
    print("🚀 Probando API GesNeu")
    print("=" * 50)
    
    # Endpoints básicos
    print("\n🧪 Endpoints básicos:")
    test_endpoint(f"{base_url}/", "Root endpoint")
    test_endpoint(f"{base_url}/health", "Health check")
    test_endpoint(f"{base_url}/docs", "Swagger docs")
    
    # Endpoints de módulos
    print("\n🧪 Módulos principales:")
    test_endpoint(f"{base_url}/auth/usuarios", "Auth - Usuarios")
    test_endpoint(f"{base_url}/catalogos/proveedores", "Catalogos - Proveedores")
    test_endpoint(f"{base_url}/vehiculos", "Vehiculos")
    test_endpoint(f"{base_url}/neumaticos", "Neumaticos")
    
    # Nuevos módulos
    print("\n🧪 Nuevos módulos:")
    test_endpoint(f"{base_url}/inventario", "Inventario")
    test_endpoint(f"{base_url}/eventos", "Eventos")
    test_endpoint(f"{base_url}/garantias", "Garantias")
    test_endpoint(f"{base_url}/alertas", "Alertas")
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas completadas")

if __name__ == "__main__":
    main()
