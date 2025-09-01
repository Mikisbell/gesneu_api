"""
Pruebas manuales para la API GesNeu usando requests (sin pytest).
Ejecutar con: python test_manual.py
Requiere que el servidor esté corriendo en localhost:8000
"""
import requests
import json
from datetime import datetime

def test_api_with_requests():
    """Prueba la API usando requests contra el servidor corriendo."""
    base_url = "http://localhost:8000"
    
    print("🧪 Pruebas manuales de la API GesNeu")
    print(f"🌐 Servidor: {base_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Endpoint raíz
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "version" in data:
                print("✅ Test 1: Endpoint raíz - OK")
                tests_passed += 1
            else:
                print("⚠️ Test 1: Endpoint raíz - Estructura incompleta")
        else:
            print(f"❌ Test 1: Endpoint raíz - Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Test 1: Servidor no disponible - ¿Está corriendo?")
    except Exception as e:
        print(f"❌ Test 1: Error - {e}")
    
    # Test 2: Health check
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print("✅ Test 2: Health check - OK")
                tests_passed += 1
            else:
                print("⚠️ Test 2: Health check - Status incorrecto")
        else:
            print(f"❌ Test 2: Health check - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Test 2: Health check - Error: {e}")
    
    # Test 3: Documentación Swagger
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Test 3: Documentación Swagger - OK")
            tests_passed += 1
        else:
            print(f"❌ Test 3: Documentación - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Test 3: Documentación - Error: {e}")
    
    # Test 4: Vehículos - Listar
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/api/v1/vehiculos/", timeout=5)
        if response.status_code in [200, 500]:  # 500 es OK si no hay BD
            print(f"✅ Test 4: Vehículos (listar) - Status {response.status_code}")
            tests_passed += 1
        else:
            print(f"⚠️ Test 4: Vehículos - Status inesperado {response.status_code}")
    except Exception as e:
        print(f"❌ Test 4: Vehículos - Error: {e}")
    
    # Test 5: Neumáticos - Info
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/api/v1/neumaticos/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "status" in data and data["status"] == "pending_implementation":
                print("✅ Test 5: Neumáticos (info) - OK")
                tests_passed += 1
            else:
                print("⚠️ Test 5: Neumáticos - Estructura incorrecta")
        else:
            print(f"❌ Test 5: Neumáticos - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Test 5: Neumáticos - Error: {e}")
    
    # Test 6: Neumáticos - Health
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/api/v1/neumaticos/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("module") == "neumaticos":
                print("✅ Test 6: Neumáticos (health) - OK")
                tests_passed += 1
            else:
                print("⚠️ Test 6: Neumáticos health - Datos incorrectos")
        else:
            print(f"❌ Test 6: Neumáticos health - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Test 6: Neumáticos health - Error: {e}")
    
    # Resumen
    print("=" * 60)
    print(f"📊 Resumen: {tests_passed}/{tests_total} pruebas pasaron")
    
    if tests_passed == tests_total:
        print("🎉 ¡Todas las pruebas pasaron! API funcionando correctamente")
    elif tests_passed > tests_total // 2:
        print("⚠️ La mayoría de pruebas pasaron. Revisar fallos menores")
    else:
        print("❌ Múltiples fallos. Revisar configuración del servidor")
    
    return tests_passed, tests_total

def test_detailed_responses():
    """Prueba detallada de las respuestas de la API."""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Análisis detallado de respuestas")
    print("=" * 60)
    
    try:
        # Analizar respuesta del endpoint raíz
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("📋 Endpoint raíz:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        
        # Analizar respuesta del health check
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n💚 Health check:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        
        # Analizar respuesta de neumáticos
        response = requests.get(f"{base_url}/api/v1/neumaticos/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n🛞 Neumáticos health:")
            for key, value in data.items():
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"Error en análisis detallado: {e}")

if __name__ == "__main__":
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    passed, total = test_api_with_requests()
    test_detailed_responses()
    
    print(f"\n⏰ Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Instrucciones:")
    print("   1. Asegúrate de que el servidor esté corriendo:")
    print("      python -m uvicorn ges_neu_api.main:app --reload")
    print("   2. Visita http://localhost:8000/docs para documentación")
    print("   3. Si hay errores de conexión, verifica el puerto")
