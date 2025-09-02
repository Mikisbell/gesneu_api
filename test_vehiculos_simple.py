#!/usr/bin/env python3
"""
Script simple para probar endpoints de vehículos - ACTUALIZADO
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/vehiculos"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NjgyNDgxOX0.1fmAvKbMorKg1sLxskLSzlspBxakPO0Y87szZVqOo8o"
headers = {'Authorization': f'Bearer {JWT_TOKEN}'}

def test_endpoint(endpoint, name):
    """Prueba un endpoint específico con debug detallado"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Probando: {name}")
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS: {len(data)} elementos")
                if data and len(data) > 0:
                    print(f"Primer elemento: {json.dumps(data[0], indent=2, default=str)[:200]}...")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON Error: {e}")
                print(f"Raw response: {response.text[:200]}...")
                return False
        elif response.status_code == 500:
            print(f"❌ SERVER ERROR 500")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ ERROR {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Servidor no responde")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - ¿Servidor corriendo?")
        return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Pruebas detalladas de vehículos")
    print(f"🔑 Token: {JWT_TOKEN[:50]}...")
    
    endpoints = [
        ("/", "Lista Vehículos"),
        ("/tipos", "Tipos Vehículo"),
        ("/configuraciones-eje", "Configuraciones Eje"),
        ("/posiciones-neumatico", "Posiciones Neumático")
    ]
    
    results = []
    for endpoint, name in endpoints:
        success = test_endpoint(endpoint, name)
        results.append((name, success))
    
    print("\n" + "=" * 60)
    print("RESUMEN FINAL:")
    for name, success in results:
        status = "✅ OK" if success else "❌ FALLO"
        print(f"  {status} {name}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\nResultado: {success_count}/{len(results)} endpoints funcionando")
    
    if success_count == len(results):
        print("🎉 ¡TODOS LOS ENDPOINTS DE VEHÍCULOS FUNCIONANDO!")
    else:
        print("⚠️  Algunos endpoints requieren corrección")
    
    # Estos endpoints anteriormente daban error 422
    problematic_endpoints = ["/tipos", "/configuraciones-eje", "/posiciones-neumatico"]
    
    for endpoint in problematic_endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - RESUELTO (Status 200)")
            else:
                print(f"   ❌ {endpoint} - AÚN CON PROBLEMAS (Status {response.status_code})")
        except:
            print(f"   ❌ {endpoint} - ERROR DE CONEXIÓN")

if __name__ == "__main__":
    main()
