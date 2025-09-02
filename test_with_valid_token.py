#!/usr/bin/env python3
"""
Pruebas completas de la API GesNeu con token JWT válido
Respeta el esquema de BD definido en ESQUEMA_COMPLETO_BD.md
"""

import requests
import json
from datetime import datetime
import uuid

# Configuración
BASE_URL = "http://127.0.0.1:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc2MzU2N30.xdMXvqDptUHd5dmbRHydch7wAvTMYFgI3AK9pn1AaYc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None, description=""):
    """Función helper para probar endpoints"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"📍 {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code < 400:
            try:
                result = response.json()
                print(f"✅ Respuesta exitosa:")
                print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
                if len(json.dumps(result, indent=2)) > 500:
                    print("... (respuesta truncada)")
                return result
            except:
                print(f"✅ Respuesta exitosa (no JSON): {response.text[:200]}")
                return response.text
        else:
            print(f"❌ Error: {response.text}")
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
    
    # 2. Verificar documentación
    test_endpoint("GET", "/docs", description="Acceder a documentación OpenAPI")
    
    # 3. Probar endpoints de autenticación
    test_endpoint("GET", "/api/v1/auth/me", description="Obtener información del usuario actual")
    
    # 4. Probar endpoints de catálogos (según esquema BD)
    print("\n" + "="*80)
    print("📋 PROBANDO MÓDULO DE CATÁLOGOS")
    
    # Proveedores
    test_endpoint("GET", "/api/v1/catalogos/proveedores", description="Listar proveedores")
    
    proveedor_data = {
        "nombre": "Proveedor Test",
        "codigo": f"PROV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "contacto": "Juan Pérez",
        "telefono": "555-1234",
        "email": "test@proveedor.com",
        "direccion": "Calle Test 123",
        "activo": True
    }
    nuevo_proveedor = test_endpoint("POST", "/api/v1/catalogos/proveedores", 
                                   proveedor_data, "Crear nuevo proveedor")
    
    # Almacenes
    test_endpoint("GET", "/api/v1/catalogos/almacenes", description="Listar almacenes")
    
    almacen_data = {
        "nombre": "Almacén Test",
        "codigo": f"ALM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "ubicacion": "Zona Industrial",
        "responsable": "María García",
        "activo": True
    }
    test_endpoint("POST", "/api/v1/catalogos/almacenes", 
                  almacen_data, "Crear nuevo almacén")
    
    # Motivos de desecho
    test_endpoint("GET", "/api/v1/catalogos/motivos-desecho", description="Listar motivos de desecho")
    
    # Parámetros de inventario
    test_endpoint("GET", "/api/v1/catalogos/parametros-inventario", description="Listar parámetros de inventario")
    
    # 5. Probar endpoints de vehículos (según esquema BD)
    print("\n" + "="*80)
    print("🚗 PROBANDO MÓDULO DE VEHÍCULOS")
    
    test_endpoint("GET", "/api/v1/vehiculos", description="Listar vehículos")
    test_endpoint("GET", "/api/v1/vehiculos/tipos", description="Listar tipos de vehículo")
    
    # 6. Probar endpoints de neumáticos (según esquema BD)
    print("\n" + "="*80)
    print("🛞 PROBANDO MÓDULO DE NEUMÁTICOS")
    
    test_endpoint("GET", "/api/v1/neumaticos", description="Listar neumáticos")
    test_endpoint("GET", "/api/v1/neumaticos/fabricantes", description="Listar fabricantes de neumáticos")
    test_endpoint("GET", "/api/v1/neumaticos/modelos", description="Listar modelos de neumáticos")
    
    # 7. Probar endpoints de inventario (según esquema BD)
    print("\n" + "="*80)
    print("📦 PROBANDO MÓDULO DE INVENTARIO")
    
    test_endpoint("GET", "/api/v1/inventario/neumaticos", description="Consultar inventario de neumáticos")
    test_endpoint("GET", "/api/v1/inventario/movimientos", description="Consultar movimientos de inventario")
    
    # 8. Probar endpoints de eventos (según esquema BD)
    print("\n" + "="*80)
    print("📅 PROBANDO MÓDULO DE EVENTOS")
    
    test_endpoint("GET", "/api/v1/eventos/neumaticos", description="Consultar eventos de neumáticos")
    test_endpoint("GET", "/api/v1/eventos/historial-estados", description="Consultar historial de estados")
    test_endpoint("GET", "/api/v1/eventos/mediciones", description="Consultar mediciones de profundidad")
    
    # 9. Probar endpoints de garantías (según esquema BD)
    print("\n" + "="*80)
    print("🛡️ PROBANDO MÓDULO DE GARANTÍAS")
    
    test_endpoint("GET", "/api/v1/garantias", description="Consultar garantías de neumáticos")
    
    # 10. Probar endpoints de alertas (según esquema BD)
    print("\n" + "="*80)
    print("🚨 PROBANDO MÓDULO DE ALERTAS")
    
    test_endpoint("GET", "/api/v1/alertas", description="Consultar alertas del sistema")
    
    # 11. Probar endpoints de bitácoras (según esquema BD)
    print("\n" + "="*80)
    print("📝 PROBANDO MÓDULO DE BITÁCORAS")
    
    test_endpoint("GET", "/api/v1/bitacoras/mantenimiento", description="Consultar bitácora de mantenimiento")
    test_endpoint("GET", "/api/v1/bitacoras/operaciones", description="Consultar bitácora de operaciones")
    
    print("\n" + "="*80)
    print("🎯 PRUEBAS COMPLETADAS")
    print("Revisa los resultados arriba para identificar endpoints funcionales y problemas")

if __name__ == "__main__":
    main()
