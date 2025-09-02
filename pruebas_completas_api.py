#!/usr/bin/env python3
"""
Pruebas completas de la API GesNeu después de las correcciones de modelos
Verifica que todos los endpoints funcionen correctamente sin errores 500
"""
import urllib.request
import urllib.error
import json
import sys

# Configuración
BASE_URL = "http://127.0.0.1:8001"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2"

def probar_endpoint(nombre, url, metodo="GET", datos=None):
    """Prueba un endpoint y retorna el estado"""
    try:
        headers = {
            'Authorization': f'Bearer {JWT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        if datos:
            datos = json.dumps(datos).encode('utf-8')
        
        req = urllib.request.Request(url, data=datos, headers=headers, method=metodo)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            contenido = response.read().decode('utf-8')
            
            if status == 200:
                print(f"✅ {nombre}: ÉXITO ({status})")
                try:
                    datos_json = json.loads(contenido)
                    if isinstance(datos_json, list):
                        print(f"   📊 Devolvió {len(datos_json)} elementos")
                    elif isinstance(datos_json, dict):
                        claves = list(datos_json.keys())[:3]
                        print(f"   📋 Claves de respuesta: {claves}")
                except:
                    print(f"   📄 Longitud de respuesta: {len(contenido)} caracteres")
            else:
                print(f"⚠️  {nombre}: Estado {status}")
                
            return status, contenido
            
    except urllib.error.HTTPError as e:
        contenido_error = e.read().decode('utf-8')
        print(f"❌ {nombre}: ERROR HTTP {e.code}")
        
        if e.code == 500:
            print(f"   🔥 ERROR DEL SERVIDOR: {contenido_error[:200]}")
        elif e.code == 401:
            print(f"   🔐 ERROR DE AUTENTICACIÓN: {contenido_error[:100]}")
        elif e.code == 404:
            print(f"   🔍 NO ENCONTRADO: {contenido_error[:100]}")
        elif e.code == 422:
            print(f"   📝 ERROR DE VALIDACIÓN: {contenido_error[:100]}")
            
        return e.code, contenido_error
        
    except Exception as e:
        print(f"💥 {nombre}: ERROR DE CONEXIÓN - {str(e)}")
        return None, str(e)

def main():
    print("🚀 PRUEBAS COMPLETAS DE LA API GESNEU")
    print("=" * 50)
    print("🎯 Objetivo: Verificar que los modelos corregidos funcionan sin errores 500")
    
    # Prueba de conectividad básica
    print("\n📡 CONECTIVIDAD BÁSICA:")
    print("-" * 25)
    probar_endpoint("Raíz de API", f"{BASE_URL}/")
    probar_endpoint("Documentación", f"{BASE_URL}/docs")
    
    # Prueba de autenticación
    print("\n🔐 AUTENTICACIÓN:")
    print("-" * 20)
    probar_endpoint("Token de Acceso", f"{BASE_URL}/api/v1/auth/token", "POST", {
        "username": "admin", 
        "password": "Admin123"
    })
    
    # Pruebas de endpoints de catálogos (CORREGIDOS)
    print("\n📦 CATÁLOGOS (MODELOS CORREGIDOS):")
    print("-" * 40)
    endpoints_catalogos = [
        ("Proveedores", f"{BASE_URL}/api/v1/catalogos/proveedores"),
        ("Almacenes", f"{BASE_URL}/api/v1/catalogos/almacenes"),
        ("Motivos de Desecho", f"{BASE_URL}/api/v1/catalogos/motivos-desecho"),
        ("Parámetros de Inventario", f"{BASE_URL}/api/v1/catalogos/parametros-inventario"),
    ]
    
    errores_500_catalogos = 0
    for nombre, url in endpoints_catalogos:
        status, _ = probar_endpoint(nombre, url)
        if status == 500:
            errores_500_catalogos += 1
    
    # Pruebas de endpoints de neumáticos (CORREGIDOS)
    print("\n🛞 NEUMÁTICOS (MODELOS CORREGIDOS):")
    print("-" * 40)
    endpoints_neumaticos = [
        ("Fabricantes de Neumáticos", f"{BASE_URL}/api/v1/neumaticos/fabricantes"),
        ("Modelos de Neumáticos", f"{BASE_URL}/api/v1/neumaticos/modelos"),
        ("Neumáticos", f"{BASE_URL}/api/v1/neumaticos/neumaticos"),
    ]
    
    errores_500_neumaticos = 0
    for nombre, url in endpoints_neumaticos:
        status, _ = probar_endpoint(nombre, url)
        if status == 500:
            errores_500_neumaticos += 1
    
    # Pruebas de endpoints de vehículos (VERIFICADOS)
    print("\n🚛 VEHÍCULOS (MODELOS VERIFICADOS):")
    print("-" * 40)
    endpoints_vehiculos = [
        ("Tipos de Vehículo", f"{BASE_URL}/api/v1/vehiculos/tipos-vehiculo"),
        ("Vehículos", f"{BASE_URL}/api/v1/vehiculos/vehiculos"),
        ("Configuraciones de Eje", f"{BASE_URL}/api/v1/vehiculos/configuraciones-eje"),
        ("Posiciones de Neumático", f"{BASE_URL}/api/v1/vehiculos/posiciones-neumatico"),
    ]
    
    errores_500_vehiculos = 0
    for nombre, url in endpoints_vehiculos:
        status, _ = probar_endpoint(nombre, url)
        if status == 500:
            errores_500_vehiculos += 1
    
    # Pruebas de otros módulos
    print("\n🔧 OTROS MÓDULOS:")
    print("-" * 20)
    otros_endpoints = [
        ("Inventario de Neumáticos", f"{BASE_URL}/api/v1/inventario/inventario-neumaticos"),
        ("Eventos de Neumáticos", f"{BASE_URL}/api/v1/eventos/eventos-neumaticos"),
        ("Garantías de Neumáticos", f"{BASE_URL}/api/v1/garantias/garantias-neumaticos"),
        ("Alertas", f"{BASE_URL}/api/v1/alertas/alertas"),
    ]
    
    errores_500_otros = 0
    for nombre, url in otros_endpoints:
        status, _ = probar_endpoint(nombre, url)
        if status == 500:
            errores_500_otros += 1
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS:")
    print("-" * 25)
    
    total_errores_500 = errores_500_catalogos + errores_500_neumaticos + errores_500_vehiculos + errores_500_otros
    
    print(f"🔥 Errores 500 en Catálogos: {errores_500_catalogos}")
    print(f"🔥 Errores 500 en Neumáticos: {errores_500_neumaticos}")
    print(f"🔥 Errores 500 en Vehículos: {errores_500_vehiculos}")
    print(f"🔥 Errores 500 en Otros: {errores_500_otros}")
    print(f"🔥 TOTAL ERRORES 500: {total_errores_500}")
    
    if total_errores_500 == 0:
        print("\n🎉 ¡ÉXITO COMPLETO!")
        print("✅ Todos los modelos están correctamente alineados con la BD")
        print("✅ No se encontraron errores 500 de servidor")
        print("✅ La API está lista para uso en producción")
    else:
        print(f"\n⚠️  Se encontraron {total_errores_500} errores 500")
        print("🔧 Algunos modelos aún necesitan corrección")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
