"""
Test de endpoints de la API GesNeu
Prueba todos los endpoints REST sin conexión a BD
"""
import os
import requests
import json
from time import sleep

# Skip DB init for testing
os.environ['SKIP_DB_INIT'] = '1'

BASE_URL = "http://localhost:8001"

def test_health_endpoint():
    """Prueba endpoint de salud"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_docs_endpoint():
    """Prueba endpoint de documentación"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ Docs endpoint: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Docs endpoint error: {e}")
        return False

def test_auth_endpoints():
    """Prueba endpoints de autenticación"""
    endpoints = [
        "/auth/usuarios",
        "/auth/roles", 
        "/auth/permisos"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")

def test_catalogos_endpoints():
    """Prueba endpoints de catálogos"""
    endpoints = [
        "/catalogos/proveedores",
        "/catalogos/almacenes",
        "/catalogos/motivos-desecho",
        "/catalogos/parametros-inventario"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")

def test_vehiculos_endpoints():
    """Prueba endpoints de vehículos"""
    endpoints = [
        "/vehiculos",
        "/vehiculos/tipos",
        "/vehiculos/configuraciones-eje",
        "/vehiculos/posiciones-neumatico",
        "/vehiculos/registros-odometro"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")

def test_neumaticos_endpoints():
    """Prueba endpoints de neumáticos"""
    endpoints = [
        "/neumaticos",
        "/neumaticos/fabricantes",
        "/neumaticos/modelos"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")

def test_new_modules_endpoints():
    """Prueba endpoints de módulos nuevos"""
    modules = [
        ("inventario", ["/inventario", "/inventario/movimientos"]),
        ("eventos", ["/eventos", "/eventos/historial", "/eventos/mediciones"]),
        ("garantias", ["/garantias"]),
        ("alertas", ["/alertas"])
    ]
    
    for module_name, endpoints in modules:
        print(f"\n🧪 Probando módulo {module_name}:")
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                print(f"✅ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} error: {e}")

def wait_for_server():
    """Espera a que el servidor esté disponible"""
    print("⏳ Esperando que el servidor esté disponible...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Servidor disponible")
                return True
        except:
            pass
        sleep(1)
    print("❌ Servidor no disponible")
    return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de endpoints GesNeu API")
    print("=" * 60)
    
    if not wait_for_server():
        print("❌ No se puede conectar al servidor")
        exit(1)
    
    print("\n🧪 Probando endpoints básicos:")
    test_health_endpoint()
    test_docs_endpoint()
    
    print("\n🧪 Probando módulos existentes:")
    test_auth_endpoints()
    test_catalogos_endpoints() 
    test_vehiculos_endpoints()
    test_neumaticos_endpoints()
    
    print("\n🧪 Probando módulos nuevos:")
    test_new_modules_endpoints()
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBAS DE ENDPOINTS COMPLETADAS")
    print("📊 Revisa los resultados arriba para ver el estado de cada endpoint")
