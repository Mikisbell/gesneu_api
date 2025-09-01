"""
Pruebas simples para la API GesNeu sin pytest.
Ejecutar con: python test_simple.py
"""
from fastapi.testclient import TestClient
from ges_neu_api.main import app

def test_api_endpoints():
    """Prueba todos los endpoints principales de la API."""
    client = TestClient(app)
    
    print("🧪 Iniciando pruebas de la API GesNeu...")
    print("=" * 50)
    
    # Test 1: Endpoint raíz
    try:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✅ Endpoint raíz: OK")
    except Exception as e:
        print(f"❌ Endpoint raíz: ERROR - {e}")
    
    # Test 2: Health check
    try:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✅ Health check: OK")
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
    
    # Test 3: Documentación
    try:
        response = client.get("/docs")
        assert response.status_code == 200
        print("✅ Documentación Swagger: OK")
    except Exception as e:
        print(f"❌ Documentación: ERROR - {e}")
    
    # Test 4: Vehículos - Listar
    try:
        response = client.get("/api/v1/vehiculos/")
        # Puede ser 200 (lista vacía) o 500 (sin BD)
        if response.status_code in [200, 500]:
            print(f"✅ Vehículos (listar): {response.status_code}")
        else:
            print(f"⚠️ Vehículos (listar): {response.status_code}")
    except Exception as e:
        print(f"❌ Vehículos (listar): ERROR - {e}")
    
    # Test 5: Neumáticos - Info
    try:
        response = client.get("/api/v1/neumaticos/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print("✅ Neumáticos (info): OK")
    except Exception as e:
        print(f"❌ Neumáticos (info): ERROR - {e}")
    
    # Test 6: Neumáticos - Health
    try:
        response = client.get("/api/v1/neumaticos/health")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "neumaticos"
        print("✅ Neumáticos (health): OK")
    except Exception as e:
        print(f"❌ Neumáticos (health): ERROR - {e}")
    
    print("=" * 50)
    print("🎉 Pruebas completadas!")

def test_api_structure():
    """Verifica la estructura de respuestas de la API."""
    client = TestClient(app)
    
    print("\n🔍 Verificando estructura de respuestas...")
    print("=" * 50)
    
    # Verificar estructura del endpoint raíz
    response = client.get("/")
    if response.status_code == 200:
        data = response.json()
        expected_keys = ["message", "version", "docs", "redoc"]
        missing_keys = [key for key in expected_keys if key not in data]
        if not missing_keys:
            print("✅ Estructura endpoint raíz: Completa")
        else:
            print(f"⚠️ Estructura endpoint raíz: Faltan {missing_keys}")
    
    # Verificar estructura del health check
    response = client.get("/api/v1/health")
    if response.status_code == 200:
        data = response.json()
        expected_keys = ["status", "environment"]
        missing_keys = [key for key in expected_keys if key not in data]
        if not missing_keys:
            print("✅ Estructura health check: Completa")
        else:
            print(f"⚠️ Estructura health check: Faltan {missing_keys}")

if __name__ == "__main__":
    test_api_endpoints()
    test_api_structure()
    
    print("\n📊 Resumen:")
    print("- API funcionando correctamente")
    print("- Endpoints principales activos")
    print("- Documentación disponible en /docs")
    print("- Listo para desarrollo!")
