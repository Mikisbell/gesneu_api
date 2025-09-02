"""
Script corregido para probar la API GesNeu con token válido
"""
import requests
import json

# Configuración con token válido
BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc2MTYzN30.JFSX0Jso15pBMYnotBmA30XxmwBNN4yEUuIc3aoGSW8"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None, description=""):
    """Función helper para probar endpoints"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        status_icon = "✅" if response.status_code < 400 else "❌"
        print(f"{status_icon} {method} {endpoint} - {response.status_code} - {description}")
        
        if response.status_code >= 400:
            print(f"   Error: {response.text[:200]}")
        elif response.status_code < 300 and method == "GET":
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   Datos: {len(data)} registros encontrados")
                else:
                    print(f"   Datos: {type(data).__name__}")
            except:
                print(f"   Respuesta: OK")
        return response
    except Exception as e:
        print(f"❌ {method} {endpoint} - ERROR: {str(e)}")
        return None

def main():
    print("🚀 PRUEBAS CORREGIDAS API GESNEU")
    print("Token JWT válido actualizado")
    print("=" * 60)
    
    # 1. Test básico de conectividad
    print("\n🔍 1. CONECTIVIDAD")
    test_endpoint("GET", "/health", description="Health check")
    test_endpoint("GET", "/api/v1/health", description="Health check v1")
    
    # 2. AUTH con token válido
    print("\n📋 2. MÓDULO AUTH")
    test_endpoint("GET", "/api/v1/auth/users/", description="Usuarios")
    test_endpoint("GET", "/api/v1/auth/roles/", description="Roles")
    test_endpoint("GET", "/api/v1/auth/permisos/", description="Permisos")
    
    # 3. Vehículos (corregido dependencias)
    print("\n🚗 3. MÓDULO VEHÍCULOS")
    test_endpoint("GET", "/api/v1/vehiculos/", description="Vehículos")
    
    # 4. Catálogos (funcionando)
    print("\n📦 4. MÓDULO CATÁLOGOS")
    test_endpoint("GET", "/api/v1/catalogos/proveedores/", description="Proveedores")
    test_endpoint("GET", "/api/v1/catalogos/almacenes/", description="Almacenes")
    test_endpoint("GET", "/api/v1/catalogos/motivos-desecho/", description="Motivos desecho")
    test_endpoint("GET", "/api/v1/catalogos/parametros-inventario/", description="Parámetros inventario")
    
    # 5. Neumáticos (corregido dependencias)
    print("\n🛞 5. MÓDULO NEUMÁTICOS")
    test_endpoint("GET", "/api/v1/neumaticos/", description="Neumáticos")
    test_endpoint("GET", "/api/v1/neumaticos/fabricantes", description="Fabricantes")
    test_endpoint("GET", "/api/v1/neumaticos/modelos", description="Modelos")
    
    # 6. Bitácoras (funcionando)
    print("\n📝 6. MÓDULO BITÁCORAS")
    test_endpoint("GET", "/api/v1/bitacoras/mantenimiento", description="Bitácora mantenimiento")
    test_endpoint("GET", "/api/v1/bitacoras/operaciones", description="Bitácora operaciones")
    test_endpoint("GET", "/api/v1/bitacoras/auditoria", description="Auditoría log")
    test_endpoint("GET", "/api/v1/bitacoras/errores", description="Errores aplicación")
    
    # 7. Sistema (parcialmente funcionando)
    print("\n⚙️ 7. MÓDULO SISTEMA")
    test_endpoint("GET", "/api/v1/sistema/parametros", description="Parámetros sistema")
    test_endpoint("GET", "/api/v1/sistema/tareas", description="Tareas programadas")
    test_endpoint("GET", "/api/v1/sistema/rutas", description="Rutas")
    test_endpoint("GET", "/api/v1/sistema/tipos-ruta", description="Tipos ruta")
    
    # 8. Módulos nuevos
    print("\n🔧 8. MÓDULOS NUEVOS")
    test_endpoint("GET", "/api/v1/inventario/stock/bajo", description="Inventario stock bajo")
    test_endpoint("GET", "/api/v1/eventos/", description="Eventos (endpoint base)")
    test_endpoint("GET", "/api/v1/garantias/vigentes", description="Garantías vigentes")
    test_endpoint("GET", "/api/v1/alertas/", description="Alertas")
    
    # 9. Test de creación con campos correctos
    print("\n🔧 9. PRUEBAS DE CREACIÓN")
    
    # Crear proveedor con campos del esquema real
    proveedor_data = {
        "nombre": "Proveedor Test Corregido",
        "tipo": "DISTRIBUIDOR",
        "ruc": "20123456789",
        "contacto_principal": "Juan Pérez",
        "telefono": "123456789",
        "email": "test@proveedor.com",
        "direccion": "Av. Test 123"
    }
    test_endpoint("POST", "/api/v1/catalogos/proveedores/", 
                  data=proveedor_data, description="Crear proveedor")
    
    print("\n" + "=" * 60)
    print("🎯 PRUEBAS CORREGIDAS COMPLETADAS")

if __name__ == "__main__":
    main()
