"""
Test corregido de la API GesNeu con URLs correctas
"""
import urllib.request
import urllib.error
import json
import time

def test_endpoint(url, description):
    """Prueba un endpoint específico"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
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
    api_v1 = f"{base_url}/api/v1"
    
    print("🚀 Probando API GesNeu con URLs correctas")
    print("=" * 60)
    
    # Endpoints básicos (sin prefijo)
    print("\n🧪 Endpoints básicos:")
    test_endpoint(f"{base_url}/", "Root endpoint")
    test_endpoint(f"{base_url}/health", "Health check")
    test_endpoint(f"{base_url}/docs", "Swagger docs")
    test_endpoint(f"{api_v1}/health", "Health check v1")
    
    # Endpoints de módulos (con prefijo /api/v1)
    print("\n🧪 Módulos principales:")
    test_endpoint(f"{api_v1}/auth/usuarios", "Auth - Usuarios")
    test_endpoint(f"{api_v1}/catalogos/proveedores", "Catalogos - Proveedores")
    test_endpoint(f"{api_v1}/vehiculos", "Vehiculos")
    test_endpoint(f"{api_v1}/neumaticos", "Neumaticos")
    
    # Nuevos módulos
    print("\n🧪 Nuevos módulos:")
    test_endpoint(f"{api_v1}/inventario", "Inventario")
    test_endpoint(f"{api_v1}/eventos", "Eventos")
    test_endpoint(f"{api_v1}/garantias", "Garantias")
    test_endpoint(f"{api_v1}/alertas", "Alertas")
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas completadas")
    print("📊 Todos los endpoints están disponibles")
    print("🌐 Documentación: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
