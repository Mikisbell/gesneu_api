#!/usr/bin/env python3
"""
Pruebas simples de endpoints con token JWT válido
Sin dependencias externas, usando urllib
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc2MzU2N30.xdMXvqDptUHd5dmbRHydch7wAvTMYFgI3AK9pn1AaYc"

def test_endpoint(method, endpoint, data=None, description=""):
    """Función helper para probar endpoints usando urllib"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"📍 {method} {endpoint}")
    
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        
        if method == "GET":
            req = urllib.request.Request(url, headers=headers)
        elif method == "POST":
            json_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"📊 Status: {status_code}")
            
            if status_code < 400:
                try:
                    result = json.loads(response_data)
                    print(f"✅ Respuesta exitosa:")
                    print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
                    if len(response_data) > 500:
                        print("... (respuesta truncada)")
                    return result
                except:
                    print(f"✅ Respuesta exitosa (no JSON): {response_data[:200]}")
                    return response_data
            else:
                print(f"❌ Error: {response_data}")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"💥 Excepción: {str(e)}")
        return None

def main():
    print("🚀 INICIANDO PRUEBAS DE API GESNEU CON TOKEN VÁLIDO")
    print(f"🔑 Token: {TOKEN[:50]}...")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # 1. Verificar estado del servidor
    test_endpoint("GET", "/", description="Verificar estado del servidor")
    
    # 2. Verificar información del usuario actual
    test_endpoint("GET", "/api/v1/auth/me", description="Obtener información del usuario actual")
    
    # 3. Probar endpoints de catálogos
    print("\n" + "="*80)
    print("📋 PROBANDO MÓDULO DE CATÁLOGOS")
    
    test_endpoint("GET", "/api/v1/catalogos/proveedores", description="Listar proveedores")
    test_endpoint("GET", "/api/v1/catalogos/almacenes", description="Listar almacenes")
    test_endpoint("GET", "/api/v1/catalogos/motivos-desecho", description="Listar motivos de desecho")
    test_endpoint("GET", "/api/v1/catalogos/parametros-inventario", description="Listar parámetros de inventario")
    
    # 4. Probar endpoints de vehículos
    print("\n" + "="*80)
    print("🚗 PROBANDO MÓDULO DE VEHÍCULOS")
    
    test_endpoint("GET", "/api/v1/vehiculos", description="Listar vehículos")
    test_endpoint("GET", "/api/v1/vehiculos/tipos", description="Listar tipos de vehículo")
    
    # 5. Probar endpoints de neumáticos
    print("\n" + "="*80)
    print("🛞 PROBANDO MÓDULO DE NEUMÁTICOS")
    
    test_endpoint("GET", "/api/v1/neumaticos", description="Listar neumáticos")
    test_endpoint("GET", "/api/v1/neumaticos/fabricantes", description="Listar fabricantes")
    test_endpoint("GET", "/api/v1/neumaticos/modelos", description="Listar modelos")
    
    # 6. Probar endpoints de inventario
    print("\n" + "="*80)
    print("📦 PROBANDO MÓDULO DE INVENTARIO")
    
    test_endpoint("GET", "/api/v1/inventario/neumaticos", description="Consultar inventario")
    test_endpoint("GET", "/api/v1/inventario/movimientos", description="Consultar movimientos")
    
    # 7. Probar endpoints de eventos
    print("\n" + "="*80)
    print("📅 PROBANDO MÓDULO DE EVENTOS")
    
    test_endpoint("GET", "/api/v1/eventos/neumaticos", description="Consultar eventos")
    test_endpoint("GET", "/api/v1/eventos/historial-estados", description="Consultar historial")
    
    # 8. Probar endpoints de garantías
    print("\n" + "="*80)
    print("🛡️ PROBANDO MÓDULO DE GARANTÍAS")
    
    test_endpoint("GET", "/api/v1/garantias", description="Consultar garantías")
    
    # 9. Probar endpoints de alertas
    print("\n" + "="*80)
    print("🚨 PROBANDO MÓDULO DE ALERTAS")
    
    test_endpoint("GET", "/api/v1/alertas", description="Consultar alertas")
    
    print("\n" + "="*80)
    print("🎯 PRUEBAS COMPLETADAS")
    print("Revisa los resultados para identificar endpoints funcionales")

if __name__ == "__main__":
    main()
