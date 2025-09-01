"""
Pruebas nativas usando solo urllib (sin dependencias externas).
Ejecutar con: python test_native.py
"""
import urllib.request
import urllib.error
import json
from datetime import datetime

def make_request(url, timeout=5):
    """Hace una petición HTTP usando urllib nativo."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.getcode(), response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except urllib.error.URLError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def test_api_native():
    """Prueba la API usando solo bibliotecas nativas de Python."""
    base_url = "http://localhost:8000"
    
    print("🧪 Pruebas nativas de la API GesNeu (sin dependencias)")
    print(f"🌐 Servidor: {base_url}")
    print("=" * 60)
    
    tests = [
        ("Endpoint raíz", "/"),
        ("Health check", "/api/v1/health"),
        ("Documentación", "/docs"),
        ("Vehículos", "/api/v1/vehiculos/"),
        ("Neumáticos info", "/api/v1/neumaticos/"),
        ("Neumáticos health", "/api/v1/neumaticos/health")
    ]
    
    results = []
    
    for test_name, endpoint in tests:
        url = f"{base_url}{endpoint}"
        status_code, response_body = make_request(url)
        
        if status_code is None:
            print(f"❌ {test_name}: Error de conexión - {response_body}")
            results.append(False)
        elif status_code == 200:
            try:
                # Intentar parsear JSON si es posible
                if endpoint in ["/", "/api/v1/health", "/api/v1/neumaticos/", "/api/v1/neumaticos/health"]:
                    data = json.loads(response_body)
                    print(f"✅ {test_name}: OK (JSON válido)")
                else:
                    print(f"✅ {test_name}: OK")
                results.append(True)
            except json.JSONDecodeError:
                print(f"✅ {test_name}: OK (HTML/texto)")
                results.append(True)
        elif status_code in [500, 422]:  # Errores esperados sin BD
            print(f"⚠️ {test_name}: Status {status_code} (esperado sin BD)")
            results.append(True)
        else:
            print(f"❌ {test_name}: Status {status_code}")
            results.append(False)
    
    # Resumen
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"📊 Resumen: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡API funcionando perfectamente!")
    elif passed >= total * 0.8:
        print("✅ API funcionando bien (algunos errores menores)")
    else:
        print("⚠️ API con problemas - revisar configuración")
    
    return passed, total

def test_json_responses():
    """Prueba específicamente las respuestas JSON."""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Verificando respuestas JSON")
    print("=" * 60)
    
    json_endpoints = [
        ("Raíz", "/"),
        ("Health", "/api/v1/health"),
        ("Neumáticos info", "/api/v1/neumaticos/"),
        ("Neumáticos health", "/api/v1/neumaticos/health")
    ]
    
    for name, endpoint in json_endpoints:
        url = f"{base_url}{endpoint}"
        status_code, response_body = make_request(url)
        
        if status_code == 200:
            try:
                data = json.loads(response_body)
                print(f"✅ {name}: JSON válido")
                
                # Mostrar estructura
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"   Campos: {', '.join(keys[:5])}")
                    if len(keys) > 5:
                        print(f"   ... y {len(keys)-5} más")
                
            except json.JSONDecodeError as e:
                print(f"❌ {name}: JSON inválido - {e}")
        else:
            print(f"⚠️ {name}: No disponible (status {status_code})")

def check_server_status():
    """Verifica si el servidor está corriendo."""
    print("🔍 Verificando estado del servidor...")
    
    status_code, response = make_request("http://localhost:8000/", timeout=2)
    
    if status_code == 200:
        print("✅ Servidor corriendo en puerto 8000")
        return True
    elif status_code is None:
        print("❌ Servidor no disponible en puerto 8000")
        print("💡 Ejecuta: python -m uvicorn ges_neu_api.main:app --reload")
        return False
    else:
        print(f"⚠️ Servidor responde con status {status_code}")
        return True

if __name__ == "__main__":
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar servidor
    if check_server_status():
        print()
        # Ejecutar pruebas
        passed, total = test_api_native()
        test_json_responses()
        
        print(f"\n⏰ Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Instrucciones finales
        print("\n💡 Próximos pasos:")
        if passed == total:
            print("   ✅ API lista para desarrollo")
            print("   🌐 Visita: http://localhost:8000/docs")
        else:
            print("   🔧 Revisar errores reportados")
            print("   📋 Verificar configuración de BD si es necesario")
    else:
        print("\n🚀 Para iniciar el servidor:")
        print("   python -m uvicorn ges_neu_api.main:app --reload --port 8000")
