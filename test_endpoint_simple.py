#!/usr/bin/env python3
"""
Prueba simple de endpoint con manejo de errores detallado
"""
import urllib.request
import urllib.error
import json

def probar_proveedores():
    """Prueba el endpoint de proveedores con manejo de errores detallado"""
    url = "http://127.0.0.1:8001/api/v1/catalogos/proveedores"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2"
    
    print("🔍 Probando endpoint de proveedores...")
    print(f"📡 URL: {url}")
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            contenido = response.read().decode('utf-8')
            
            print(f"✅ ÉXITO: Estado {status}")
            print(f"📊 Contenido: {contenido[:300]}")
            
            return True
            
    except urllib.error.HTTPError as e:
        print(f"❌ ERROR HTTP: {e.code}")
        error_content = e.read().decode('utf-8')
        print(f"🔥 Detalles del error:")
        print(error_content)
        return False
        
    except Exception as e:
        print(f"💥 ERROR DE CONEXIÓN: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA SIMPLE DE ENDPOINT DE PROVEEDORES")
    print("=" * 50)
    
    resultado = probar_proveedores()
    
    if not resultado:
        print("\n⚠️  RECOMENDACIÓN:")
        print("1. Revisar los logs del servidor uvicorn en la consola")
        print("2. Verificar que la tabla 'proveedores' existe en la BD")
        print("3. Comprobar que el servicio CatalogService funciona correctamente")
    
    print("\n" + "=" * 50)
