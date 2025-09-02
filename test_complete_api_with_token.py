"""
Script completo para probar todos los endpoints de la API GesNeu
con autenticación JWT alineado con ESQUEMA_COMPLETO_BD.md
"""
import requests
import json
from datetime import datetime
import uuid

# Configuración base
BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NjczODk2NX0.h-dykTLyfmBXQa15RBEM8ZvIr0R2NWfz3X_jvaTd9jo"

# Headers con autenticación
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None, description=""):
    """Función helper para probar endpoints"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        status_icon = "✅" if response.status_code < 400 else "❌"
        print(f"{status_icon} {method} {endpoint} - {response.status_code} - {description}")
        if response.status_code >= 400:
            print(f"   Error: {response.text}")
        elif response.status_code < 300 and method == "GET":
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   Datos: {len(data)} registros encontrados")
                else:
                    print(f"   Datos: {type(data).__name__}")
            except:
                print(f"   Respuesta: {response.text[:100]}...")
        return response
    except Exception as e:
        print(f"❌ {method} {endpoint} - ERROR: {str(e)}")
        return None

def main():
    print("🚀 INICIANDO PRUEBAS COMPLETAS DE LA API GESNEU")
    print("Basado en ESQUEMA_COMPLETO_BD.md - 37 tablas reales")
    print("=" * 60)
    
    # 1. MÓDULO AUTH - Tablas: usuarios, roles, permisos, usuarios_roles, roles_permisos
    print("\n📋 1. MÓDULO AUTH (5 tablas)")
    test_endpoint("GET", "/api/v1/auth/users/", description="Tabla: usuarios")
    test_endpoint("GET", "/api/v1/auth/roles/", description="Tabla: roles")
    test_endpoint("GET", "/api/v1/auth/permisos/", description="Tabla: permisos")
    
    # 2. MÓDULO VEHÍCULOS - Tablas: vehiculos, tipos_vehiculo, configuraciones_eje, posiciones_neumatico, registros_odometro
    print("\n🚗 2. MÓDULO VEHÍCULOS (5 tablas)")
    test_endpoint("GET", "/api/v1/vehiculos/", description="Tabla: vehiculos")
    # Nota: tipos_vehiculo, configuraciones_eje, etc. son tablas separadas que necesitan endpoints específicos
    
    # 3. MÓDULO CATÁLOGOS - Tablas: proveedores, almacenes, motivos_desecho, parametros_inventario
    print("\n📦 3. MÓDULO CATÁLOGOS (4 tablas)")
    test_endpoint("GET", "/api/v1/catalogos/proveedores/", description="Tabla: proveedores")
    test_endpoint("GET", "/api/v1/catalogos/almacenes/", description="Tabla: almacenes")
    test_endpoint("GET", "/api/v1/catalogos/motivos-desecho/", description="Tabla: motivos_desecho")
    test_endpoint("GET", "/api/v1/catalogos/parametros-inventario/", description="Tabla: parametros_inventario")
    
    # 4. MÓDULO NEUMÁTICOS - Tablas: neumaticos, fabricantes_neumatico, modelos_neumatico
    print("\n🛞 4. MÓDULO NEUMÁTICOS (3 tablas)")
    test_endpoint("GET", "/api/v1/neumaticos/", description="Tabla: neumaticos")
    test_endpoint("GET", "/api/v1/neumaticos/fabricantes", description="Tabla: fabricantes_neumatico")
    test_endpoint("GET", "/api/v1/neumaticos/modelos", description="Tabla: modelos_neumatico")
    
    # 5. MÓDULO INVENTARIO - Tablas: inventario_neumaticos, movimientos_inventario
    print("\n📊 5. MÓDULO INVENTARIO (2 tablas)")
    test_endpoint("GET", "/api/v1/inventario/stock/bajo", description="Inventario stock bajo")
    # Nota: inventario requiere parámetros específicos (modelo_id, almacen_id)
    
    # 6. MÓDULO EVENTOS - Tablas: eventos_neumaticos, historial_estados_neumaticos, mediciones_profundidad
    print("\n📅 6. MÓDULO EVENTOS (3 tablas)")
    # Nota: eventos requieren parámetros específicos (neumatico_id, tipo_evento)
    print("   Eventos requieren parámetros específicos - endpoints disponibles")
    
    # 7. MÓDULO GARANTÍAS - Tablas: garantias_neumaticos
    print("\n🛡️ 7. MÓDULO GARANTÍAS (1 tabla)")
    test_endpoint("GET", "/api/v1/garantias/vigentes", description="Garantías vigentes")
    test_endpoint("GET", "/api/v1/garantias/por-vencer", description="Garantías por vencer")
    
    # 8. MÓDULO ALERTAS - Tablas: alertas
    print("\n🚨 8. MÓDULO ALERTAS (1 tabla)")
    test_endpoint("GET", "/api/v1/alertas/", description="Tabla: alertas")
    
    # 9. MÓDULO BITÁCORAS - Tablas: bitacora_mantenimiento, bitacora_operaciones, auditoria_log, etc.
    print("\n📝 9. MÓDULO BITÁCORAS (6+ tablas)")
    test_endpoint("GET", "/api/v1/bitacoras/mantenimiento", description="Tabla: bitacora_mantenimiento")
    test_endpoint("GET", "/api/v1/bitacoras/operaciones", description="Tabla: bitacora_operaciones")
    test_endpoint("GET", "/api/v1/bitacoras/auditoria", description="Tabla: auditoria_log")
    test_endpoint("GET", "/api/v1/bitacoras/errores", description="Tabla: errores_aplicacion")
    
    # 10. MÓDULO SISTEMA - Tablas: rutas, tipos_ruta, parametros_sistema, tareas_programadas
    print("\n⚙️ 10. MÓDULO SISTEMA (4 tablas)")
    test_endpoint("GET", "/api/v1/sistema/rutas", description="Tabla: rutas")
    test_endpoint("GET", "/api/v1/sistema/tipos-ruta", description="Tabla: tipos_ruta")
    test_endpoint("GET", "/api/v1/sistema/parametros", description="Tabla: parametros_sistema")
    test_endpoint("GET", "/api/v1/sistema/tareas", description="Tabla: tareas_programadas")
    
    # Test de creación de datos según esquema real
    print("\n🔧 PRUEBAS DE CREACIÓN (según ESQUEMA_COMPLETO_BD.md)")
    
    # Crear proveedor según esquema real
    proveedor_data = {
        "codigo": "PROV001",  # Campo requerido según esquema
        "nombre": "Proveedor Test",
        "tipo_proveedor": "DISTRIBUIDOR",  # Enum según esquema
        "contacto_principal": "Juan Pérez",
        "telefono": "123456789",
        "email": "test@proveedor.com",
        "activo": True
    }
    test_endpoint("POST", "/api/v1/catalogos/proveedores/", 
                  data=proveedor_data, description="Crear proveedor (esquema real)")
    
    # Crear almacén según esquema real
    almacen_data = {
        "codigo": "ALM001",  # Campo requerido según esquema
        "nombre": "Almacén Test",
        "tipo": "PRINCIPAL",
        "direccion": "Dirección Test",
        "activo": True
    }
    test_endpoint("POST", "/api/v1/catalogos/almacenes/", 
                  data=almacen_data, description="Crear almacén (esquema real)")
    
    print("\n" + "=" * 60)
    print("🎯 PRUEBAS COMPLETADAS")
    print("Verificando alineación con ESQUEMA_COMPLETO_BD.md")
    print("37 tablas identificadas en esquema real de PostgreSQL")

if __name__ == "__main__":
    main()
