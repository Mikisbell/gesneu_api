#!/usr/bin/env python3
"""
Script de pruebas con el nuevo token JWT proporcionado
"""
import requests
import json
import sys

# Configuración
BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc1MTExM30._N4mycyYTHbpI5s2tTozOTlIW0y2aI7vrYX7kwF40hg"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None, description=""):
    """Función helper para probar endpoints"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            print(f"❌ Método no soportado: {method}")
            return False
            
        print(f"{'✅' if response.status_code < 400 else '❌'} {method} {endpoint} - {response.status_code} - {description}")
        
        if response.status_code >= 400:
            print(f"   Error: {response.text[:200]}")
            
        return response.status_code < 400
        
    except requests.exceptions.Timeout:
        print(f"❌ {method} {endpoint} - TIMEOUT - {description}")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - ERROR: {str(e)} - {description}")
        return False

def main():
    """Ejecutar pruebas de endpoints principales"""
    print("=== Pruebas API GesNeu con Nuevo Token ===\n")
    
    # Pruebas básicas sin autenticación
    print("1. Pruebas básicas:")
    test_endpoint("GET", "/health", description="Health check")
    test_endpoint("GET", "/docs", description="Documentación")
    
    print("\n2. Pruebas de autenticación:")
    test_endpoint("GET", "/api/v1/auth/me", description="Usuario actual")
    
    print("\n3. Pruebas de catálogos:")
    test_endpoint("GET", "/api/v1/catalogos/almacenes/", description="Listar almacenes")
    test_endpoint("GET", "/api/v1/catalogos/proveedores/", description="Listar proveedores")
    
    print("\n4. Pruebas de vehículos:")
    test_endpoint("GET", "/api/v1/vehiculos/", description="Listar vehículos")
    test_endpoint("GET", "/api/v1/vehiculos/tipos/", description="Tipos de vehículo")
    
    print("\n5. Pruebas de neumáticos:")
    test_endpoint("GET", "/api/v1/neumaticos/", description="Listar neumáticos")
    test_endpoint("GET", "/api/v1/neumaticos/fabricantes/", description="Fabricantes")
    test_endpoint("GET", "/api/v1/neumaticos/modelos/", description="Modelos")
    
    print("\n6. Pruebas de bitácoras:")
    test_endpoint("GET", "/api/v1/bitacoras/operaciones/", description="Operaciones")
    
    print("\n7. Pruebas de sistema:")
    test_endpoint("GET", "/api/v1/sistema/rutas/", description="Rutas")
    test_endpoint("GET", "/api/v1/sistema/tipos-ruta/", description="Tipos de ruta")
    
    print("\n8. Pruebas de módulos nuevos:")
    test_endpoint("GET", "/api/v1/inventario/", description="Inventario")
    test_endpoint("GET", "/api/v1/eventos/", description="Eventos")
    test_endpoint("GET", "/api/v1/garantias/", description="Garantías")
    test_endpoint("GET", "/api/v1/alertas/", description="Alertas")
    
    print("\n=== Pruebas completadas ===")

if __name__ == "__main__":
    main()
