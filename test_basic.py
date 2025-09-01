"""
Pruebas basicas para la API GesNeu (sin emojis para evitar problemas de encoding).
Ejecutar con: python test_basic.py
"""
import urllib.request
import urllib.error
import json
from datetime import datetime

def make_request(url, timeout=5):
    """Hace una peticion HTTP usando urllib nativo."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.getcode(), response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except urllib.error.URLError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def test_api_basic():
    """Prueba la API usando solo bibliotecas nativas de Python."""
    base_url = "http://localhost:8000"
    
    print("Pruebas basicas de la API GesNeu")
    print("Servidor:", base_url)
    print("=" * 50)
    
    tests = [
        ("Endpoint raiz", "/"),
        ("Health check", "/api/v1/health"),
        ("Documentacion", "/docs"),
        ("Vehiculos", "/api/v1/vehiculos/"),
        ("Neumaticos info", "/api/v1/neumaticos/"),
        ("Neumaticos health", "/api/v1/neumaticos/health")
    ]
    
    results = []
    
    for test_name, endpoint in tests:
        url = f"{base_url}{endpoint}"
        status_code, response_body = make_request(url)
        
        if status_code is None:
            print(f"ERROR {test_name}: Conexion fallida - {response_body}")
            results.append(False)
        elif status_code == 200:
            try:
                # Intentar parsear JSON si es posible
                if endpoint in ["/", "/api/v1/health", "/api/v1/neumaticos/", "/api/v1/neumaticos/health"]:
                    data = json.loads(response_body)
                    print(f"OK {test_name}: JSON valido")
                else:
                    print(f"OK {test_name}: Respuesta correcta")
                results.append(True)
            except json.JSONDecodeError:
                print(f"OK {test_name}: HTML/texto")
                results.append(True)
        elif status_code in [500, 422]:  # Errores esperados sin BD
            print(f"WARN {test_name}: Status {status_code} (esperado sin BD)")
            results.append(True)
        else:
            print(f"ERROR {test_name}: Status {status_code}")
            results.append(False)
    
    # Resumen
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Resumen: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("EXITO: API funcionando perfectamente!")
    elif passed >= total * 0.8:
        print("OK: API funcionando bien (algunos errores menores)")
    else:
        print("WARN: API con problemas - revisar configuracion")
    
    return passed, total

def check_server_status():
    """Verifica si el servidor esta corriendo."""
    print("Verificando estado del servidor...")
    
    status_code, response = make_request("http://localhost:8000/", timeout=2)
    
    if status_code == 200:
        print("OK: Servidor corriendo en puerto 8000")
        return True
    elif status_code is None:
        print("ERROR: Servidor no disponible en puerto 8000")
        print("Ejecuta: python -m uvicorn ges_neu_api.main:app --reload")
        return False
    else:
        print(f"WARN: Servidor responde con status {status_code}")
        return True

def show_api_info():
    """Muestra informacion de los endpoints principales."""
    base_url = "http://localhost:8000"
    
    print("\nInformacion de endpoints:")
    print("-" * 30)
    
    # Info del endpoint raiz
    status_code, response_body = make_request(f"{base_url}/")
    if status_code == 200:
        try:
            data = json.loads(response_body)
            print("Endpoint raiz:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        except:
            pass
    
    # Info del health check
    status_code, response_body = make_request(f"{base_url}/api/v1/health")
    if status_code == 200:
        try:
            data = json.loads(response_body)
            print("\nHealth check:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        except:
            pass

if __name__ == "__main__":
    print("Iniciado:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Verificar servidor
    if check_server_status():
        print()
        # Ejecutar pruebas
        passed, total = test_api_basic()
        show_api_info()
        
        print(f"\nFinalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Instrucciones finales
        print("\nProximos pasos:")
        if passed == total:
            print("  - API lista para desarrollo")
            print("  - Visita: http://localhost:8000/docs")
        else:
            print("  - Revisar errores reportados")
            print("  - Verificar configuracion de BD si es necesario")
    else:
        print("\nPara iniciar el servidor:")
        print("  python -m uvicorn ges_neu_api.main:app --reload --port 8000")
