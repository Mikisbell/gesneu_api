#!/usr/bin/env python3
"""
Script para probar los endpoints principales de la API GesNeu
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        
    def authenticate(self):
        """Obtiene token de autenticación"""
        print("🔐 Autenticando con usuario admin...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/token",
                data={"username": "admin", "password": "Admin123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"   ✅ Autenticación exitosa")
                return True
            else:
                print(f"   ❌ Error de autenticación: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
            return False
    
    def test_endpoint(self, method, endpoint, data=None, description=""):
        """Prueba un endpoint específico"""
        print(f"\n🔍 {description}")
        print(f"   {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=self.headers, timeout=10)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=self.headers, timeout=10)
            elif method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=self.headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}", headers=self.headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code < 400:
                print(f"   ✅ ÉXITO")
                if response.content:
                    try:
                        result = response.json()
                        if isinstance(result, list):
                            print(f"   📊 Elementos devueltos: {len(result)}")
                        elif isinstance(result, dict):
                            print(f"   📋 Datos: {list(result.keys())[:5]}")
                    except:
                        print(f"   📄 Respuesta no JSON")
                return True
            else:
                try:
                    error = response.json()
                    print(f"   ❌ ERROR: {error.get('detail', 'Error desconocido')}")
                except:
                    print(f"   ❌ ERROR: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: No se puede conectar al servidor")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return False
    
    def run_tests(self):
        """Ejecuta todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DE ENDPOINTS API GESNEU")
        print("=" * 70)
        
        # Autenticación
        if not self.authenticate():
            print("❌ No se pudo autenticar. Terminando pruebas.")
            return
        
        # Pruebas de endpoints principales
        tests = [
            # Auth endpoints
            ("GET", "/auth/users/me", None, "Obtener información del usuario actual"),
            ("GET", "/auth/users", None, "Listar usuarios"),
            ("GET", "/auth/roles", None, "Listar roles"),
            ("GET", "/auth/permisos", None, "Listar permisos"),
            
            # Catalogos endpoints
            ("GET", "/catalogos/proveedores", None, "Listar proveedores"),
            ("GET", "/catalogos/almacenes", None, "Listar almacenes"),
            ("GET", "/catalogos/motivos-desecho", None, "Listar motivos de desecho"),
            ("GET", "/catalogos/parametros-inventario", None, "Listar parámetros de inventario"),
            
            # Vehiculos endpoints
            ("GET", "/vehiculos", None, "Listar vehículos"),
            ("GET", "/vehiculos/tipos", None, "Listar tipos de vehículo"),
            ("GET", "/vehiculos/configuraciones-eje", None, "Listar configuraciones de eje"),
            ("GET", "/vehiculos/posiciones-neumatico", None, "Listar posiciones de neumático"),
            
            # Neumaticos endpoints
            ("GET", "/neumaticos", None, "Listar neumáticos"),
            ("GET", "/neumaticos/fabricantes", None, "Listar fabricantes"),
            ("GET", "/neumaticos/modelos", None, "Listar modelos de neumático"),
            
            # Inventario endpoints
            ("GET", "/inventario/neumaticos", None, "Listar inventario de neumáticos"),
            ("GET", "/inventario/movimientos", None, "Listar movimientos de inventario"),
            
            # Eventos endpoints
            ("GET", "/eventos/neumaticos", None, "Listar eventos de neumáticos"),
            ("GET", "/eventos/historial-estados", None, "Listar historial de estados"),
            ("GET", "/eventos/mediciones-profundidad", None, "Listar mediciones de profundidad"),
            
            # Garantias endpoints
            ("GET", "/garantias", None, "Listar garantías"),
            
            # Alertas endpoints
            ("GET", "/alertas", None, "Listar alertas"),
        ]
        
        successful_tests = 0
        total_tests = len(tests)
        
        for method, endpoint, data, description in tests:
            if self.test_endpoint(method, endpoint, data, description):
                successful_tests += 1
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE PRUEBAS:")
        print(f"   ✅ Exitosas: {successful_tests}/{total_tests}")
        print(f"   ❌ Fallidas: {total_tests - successful_tests}/{total_tests}")
        print(f"   📈 Porcentaje de éxito: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! API lista para producción.")
        elif successful_tests > total_tests * 0.8:
            print("\n✅ La mayoría de pruebas pasaron. API en buen estado.")
        else:
            print("\n⚠️ Varias pruebas fallaron. Revisar configuración.")
        
        print("🏁 PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    tester = APITester()
    tester.run_tests()
