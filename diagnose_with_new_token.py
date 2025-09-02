#!/usr/bin/env python3
"""
Diagnóstico completo de la API GesNeu con token JWT actualizado
Sin dependencias externas, usando urllib
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc2NDM5OH0.1SC5ejRMgRyQE8HP26gLODxBsBKuhEznGfQR45BQez8"

def test_endpoint(method, endpoint, description=""):
    """Función helper para probar endpoints usando urllib"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            status_icon = "✅" if status_code == 200 else "❌"
            print(f"{status_icon} {endpoint} - {status_code} - {description}")
            
            if status_code == 200:
                try:
                    result = json.loads(response_data)
                    if isinstance(result, list):
                        print(f"   Datos: {len(result)} registros")
                    elif isinstance(result, dict):
                        print(f"   Datos: {len(result)} campos")
                    else:
                        print(f"   Datos: {type(result).__name__}")
                except:
                    print(f"   Respuesta: OK (no JSON)")
            else:
                print(f"   Error: {response_data[:150]}")
                
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"❌ {endpoint} - {e.code} - {description}")
        print(f"   Error: {error_data[:150]}")
    except Exception as e:
        print(f"❌ {endpoint} - ERROR - {description}")
        print(f"   Excepción: {str(e)}")

def main():
    print("🔍 DIAGNÓSTICO COMPLETO API GESNEU")
    print("=" * 60)
    print(f"🔑 Token: {TOKEN[:50]}...")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # 1. Test básico de conectividad
    print("\n1. TEST DE CONECTIVIDAD")
    test_endpoint("GET", "/", "Ruta raíz")
    test_endpoint("GET", "/health", "Health check")
    test_endpoint("GET", "/api/v1/health", "Health check v1")
    
    # 2. Test de autenticación
    print("\n2. TEST DE AUTENTICACIÓN")
    test_endpoint("GET", "/api/v1/auth/me", "Información del usuario")
    test_endpoint("GET", "/api/v1/auth/users/", "Lista de usuarios")
    
    # 3. Test de catálogos
    print("\n3. MÓDULO DE CATÁLOGOS")
    test_endpoint("GET", "/api/v1/catalogos/proveedores", "Proveedores")
    test_endpoint("GET", "/api/v1/catalogos/almacenes", "Almacenes")
    test_endpoint("GET", "/api/v1/catalogos/motivos-desecho", "Motivos de desecho")
    test_endpoint("GET", "/api/v1/catalogos/parametros-inventario", "Parámetros inventario")
    
    # 4. Test de vehículos
    print("\n4. MÓDULO DE VEHÍCULOS")
    test_endpoint("GET", "/api/v1/vehiculos", "Vehículos")
    test_endpoint("GET", "/api/v1/vehiculos/tipos", "Tipos de vehículo")
    
    # 5. Test de neumáticos
    print("\n5. MÓDULO DE NEUMÁTICOS")
    test_endpoint("GET", "/api/v1/neumaticos", "Neumáticos")
    test_endpoint("GET", "/api/v1/neumaticos/fabricantes", "Fabricantes")
    test_endpoint("GET", "/api/v1/neumaticos/modelos", "Modelos")
    
    # 6. Test de inventario
    print("\n6. MÓDULO DE INVENTARIO")
    test_endpoint("GET", "/api/v1/inventario/neumaticos", "Inventario neumáticos")
    test_endpoint("GET", "/api/v1/inventario/movimientos", "Movimientos inventario")
    
    # 7. Test de eventos
    print("\n7. MÓDULO DE EVENTOS")
    test_endpoint("GET", "/api/v1/eventos/neumaticos", "Eventos neumáticos")
    test_endpoint("GET", "/api/v1/eventos/historial-estados", "Historial estados")
    
    # 8. Test de garantías
    print("\n8. MÓDULO DE GARANTÍAS")
    test_endpoint("GET", "/api/v1/garantias", "Garantías")
    
    # 9. Test de alertas
    print("\n9. MÓDULO DE ALERTAS")
    test_endpoint("GET", "/api/v1/alertas", "Alertas")
    
    # 10. Test de bitácoras
    print("\n10. MÓDULO DE BITÁCORAS")
    test_endpoint("GET", "/api/v1/bitacoras/mantenimiento", "Bitácora mantenimiento")
    test_endpoint("GET", "/api/v1/bitacoras/operaciones", "Bitácora operaciones")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO COMPLETADO")
    print("Revisa los resultados para identificar problemas específicos")

if __name__ == "__main__":
    main()
