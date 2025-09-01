"""
Test simple de endpoints de la API GesNeu
Prueba endpoints básicos con curl
"""
import subprocess
import json
import time

def run_curl(url, method="GET", data=None):
    """Ejecuta curl y retorna el resultado"""
    cmd = ["curl", "-s", "-X", method, url]
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def test_basic_endpoints():
    """Prueba endpoints básicos"""
    base_url = "http://localhost:8001"
    
    endpoints = [
        "/",
        "/health", 
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    print("🧪 Probando endpoints básicos:")
    for endpoint in endpoints:
        code, stdout, stderr = run_curl(f"{base_url}{endpoint}")
        status = "✅" if code == 0 else "❌"
        print(f"{status} {endpoint}: HTTP {code}")

def test_module_endpoints():
    """Prueba endpoints de módulos"""
    base_url = "http://localhost:8001"
    
    modules = {
        "Auth": ["/auth/usuarios", "/auth/roles", "/auth/permisos"],
        "Catalogos": ["/catalogos/proveedores", "/catalogos/almacenes"],
        "Vehiculos": ["/vehiculos", "/vehiculos/tipos"],
        "Neumaticos": ["/neumaticos", "/neumaticos/fabricantes"],
        "Inventario": ["/inventario", "/inventario/movimientos"],
        "Eventos": ["/eventos", "/eventos/historial"],
        "Garantias": ["/garantias"],
        "Alertas": ["/alertas"]
    }
    
    for module_name, endpoints in modules.items():
        print(f"\n🧪 Probando módulo {module_name}:")
        for endpoint in endpoints:
            code, stdout, stderr = run_curl(f"{base_url}{endpoint}")
            status = "✅" if code == 0 else "❌"
            print(f"{status} {endpoint}: HTTP {code}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas simples de endpoints")
    print("=" * 50)
    
    # Esperar un poco para que el servidor esté listo
    time.sleep(2)
    
    test_basic_endpoints()
    test_module_endpoints()
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas de endpoints completadas")
    print("📝 Revisa los resultados arriba")
