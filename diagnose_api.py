"""
Script de diagnóstico simple para identificar problemas en la API GesNeu
"""
import requests
import sys

# Configuración
BASE_URL = "http://127.0.0.1:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc2NDM5OH0.1SC5ejRMgRyQE8HP26gLODxBsBKuhEznGfQR45BQez8"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_simple(endpoint, description):
    """Prueba simple de endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers, timeout=10)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {endpoint} - {response.status_code} - {description}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:150]}")
        else:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   Datos: {len(data)} registros")
                else:
                    print(f"   Datos: {type(data).__name__}")
            except:
                print(f"   Respuesta: OK")
    except Exception as e:
        print(f"❌ {endpoint} - ERROR: {str(e)}")

def main():
    print("🔍 DIAGNÓSTICO RÁPIDO API GESNEU")
    print("=" * 50)
    
    # Test básico de conectividad
    print("\n1. TEST DE CONECTIVIDAD")
    test_simple("/", "Ruta raíz")
    test_simple("/health", "Health check")
    test_simple("/api/v1/health", "Health check v1")
    
    # Test de autenticación
    print("\n2. TEST DE AUTENTICACIÓN")
    test_simple("/api/v1/auth/users/", "Usuarios (con token)")
    
    # Test de módulos que funcionaron
    print("\n3. MÓDULOS QUE FUNCIONAN")
    test_simple("/api/v1/catalogos/proveedores/", "Proveedores")
    test_simple("/api/v1/bitacoras/mantenimiento", "Bitácora mantenimiento")
    test_simple("/api/v1/sistema/parametros", "Parámetros sistema")
    
    # Test de módulos con problemas
    print("\n4. MÓDULOS CON PROBLEMAS")
    test_simple("/api/v1/vehiculos/", "Vehículos")
    test_simple("/api/v1/neumaticos/", "Neumáticos")
    test_simple("/api/v1/catalogos/almacenes/", "Almacenes")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main()
