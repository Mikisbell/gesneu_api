#!/usr/bin/env python3
"""
Script completo para probar TODOS los endpoints de la API GesNeu
Actualizado con nuevo token y puerto 8001
"""

import requests
import json
from datetime import datetime

# Configuración actualizada
BASE_URL = "http://localhost:8000"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njg1NjU2MH0.TD-1nLWg6AWXFGtvPdUKBw-7uazqM_ET7nKX-aABHYk"
headers = {'Authorization': f'Bearer {JWT_TOKEN}'}

def test_endpoint(endpoint, name, require_auth=True):
    """Prueba un endpoint específico"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if require_auth:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
        
        if response.status_code == 200:
            try:
                data = response.json()
                count = len(data) if isinstance(data, list) else 1
                print(f"  ✅ {name}: Status {response.status_code} ({count} elementos)")
                return True
            except:
                print(f"  ✅ {name}: Status {response.status_code} (HTML/Text)")
                return True
        else:
            print(f"  ❌ {name}: Status {response.status_code}")
            if response.status_code in [404, 500]:
                print(f"     Error: {response.text[:150]}...")
            return False
    except Exception as e:
        print(f"  💥 {name}: Error de conexión - {str(e)[:100]}")
        return False

print("🚀 === PRUEBAS COMPLETAS API GESNEU ===")
print(f"⏰ Timestamp: {datetime.now()}")
print(f"🌐 Base URL: {BASE_URL}")
print(f"🔑 Token válido hasta: Sep 2025\n")

# Endpoints del sistema (sin auth)
print("🔧 SISTEMA Y DOCUMENTACIÓN:")
system_results = []
system_endpoints = [
    ('/', 'Root Endpoint'),
    ('/docs', 'Swagger UI'),
    ('/redoc', 'ReDoc'),
    ('/health', 'Health Check')
]

for endpoint, name in system_endpoints:
    result = test_endpoint(endpoint, name, require_auth=False)
    system_results.append(result)

# Endpoints de autenticación
print("\n🔐 AUTENTICACIÓN:")
auth_results = []
auth_endpoints = [
    ('/api/v1/auth/me', 'Usuario Actual')
]

for endpoint, name in auth_endpoints:
    result = test_endpoint(endpoint, name, require_auth=True)
    auth_results.append(result)

# Endpoints de catálogos
print("\n📋 CATÁLOGOS:")
catalog_results = []
catalog_endpoints = [
    ('/api/v1/catalogos/proveedores', 'Proveedores'),
    ('/api/v1/catalogos/almacenes', 'Almacenes'),
    ('/api/v1/catalogos/motivos-desecho', 'Motivos Desecho'),
    ('/api/v1/catalogos/parametros-inventario', 'Parámetros Inventario')
]

for endpoint, name in catalog_endpoints:
    result = test_endpoint(endpoint, name, require_auth=True)
    catalog_results.append(result)

# Endpoints de vehículos
print("\n🚛 VEHÍCULOS:")
vehicle_results = []
vehicle_endpoints = [
    ('/api/v1/vehiculos/', 'Lista Vehículos'),
    ('/api/v1/vehiculos/tipos', 'Tipos Vehículo'),
    ('/api/v1/vehiculos/configuraciones-eje', 'Configuraciones Eje'),
    ('/api/v1/vehiculos/posiciones-neumatico', 'Posiciones Neumático')
]

for endpoint, name in vehicle_endpoints:
    result = test_endpoint(endpoint, name, require_auth=True)
    vehicle_results.append(result)

# Endpoints de neumáticos
print("\n🛞 NEUMÁTICOS:")
tire_results = []
tire_endpoints = [
    ('/api/v1/neumaticos/fabricantes', 'Fabricantes'),
    ('/api/v1/neumaticos/modelos', 'Modelos'),
    ('/api/v1/neumaticos/', 'Lista Neumáticos')
]

for endpoint, name in tire_endpoints:
    result = test_endpoint(endpoint, name, require_auth=True)
    tire_results.append(result)

# Endpoints de otros módulos
print("\n📦 OTROS MÓDULOS:")
other_results = []
other_endpoints = [
    ('/api/v1/inventario/neumaticos', 'Inventario'),
    ('/api/v1/eventos/', 'Eventos'),
    ('/api/v1/garantias/neumaticos', 'Garantías'),
    ('/api/v1/alertas/', 'Alertas')
]

for endpoint, name in other_endpoints:
    result = test_endpoint(endpoint, name, require_auth=True)
    other_results.append(result)

# Resumen final
print("\n📊 === RESUMEN FINAL ===")
total_tests = len(system_results) + len(auth_results) + len(catalog_results) + len(vehicle_results) + len(tire_results) + len(other_results)
total_passed = sum(system_results) + sum(auth_results) + sum(catalog_results) + sum(vehicle_results) + sum(tire_results) + sum(other_results)

print(f"🎯 Total endpoints probados: {total_tests}")
print(f"✅ Endpoints funcionando: {total_passed}")
print(f"❌ Endpoints con errores: {total_tests - total_passed}")
print(f"📈 Porcentaje de éxito: {(total_passed/total_tests)*100:.1f}%")

if total_passed == total_tests:
    print("\n🎉 ¡API COMPLETAMENTE FUNCIONAL!")
else:
    print(f"\n⚠️  {total_tests - total_passed} endpoints requieren corrección")

print(f"\n⏰ Pruebas completadas: {datetime.now()}")
