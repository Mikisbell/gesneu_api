import urllib.request
import urllib.parse
import json

def test_auth_simple(username, password):
    """Prueba simple de autenticación"""
    print(f"\n🔍 Probando autenticación:")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {'*' * len(password)}")
    
    # Preparar datos
    data = urllib.parse.urlencode({
        'username': username,
        'password': password
    }).encode('utf-8')
    
    # Crear request
    req = urllib.request.Request(
        'http://localhost:8001/api/v1/auth/token',
        data=data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        method='POST'
    )
    
    try:
        # Hacer request
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"   ✅ ÉXITO - Status: {response.status}")
            print(f"   Token tipo: {result.get('token_type')}")
            print(f"   Token: {result.get('access_token')[:50]}...")
            return result.get('access_token')
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_data = json.loads(error_body)
            print(f"   ❌ ERROR {e.code}: {error_data.get('detail')}")
        except:
            print(f"   ❌ ERROR {e.code}: {error_body}")
        return None
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    print("🚀 PRUEBAS DE AUTENTICACIÓN SIMPLES")
    print("=" * 50)
    
    # Prueba 1: Usuario inexistente
    test_auth_simple("usuario_inexistente", "password123")
    
    # Prueba 2: Admin con contraseña incorrecta  
    test_auth_simple("admin", "password_incorrecta")
    
    # Prueba 3: Admin con credenciales correctas
    token = test_auth_simple("admin", "Admin123")
    
    print("\n" + "=" * 50)
    print("🏁 PRUEBAS COMPLETADAS")
