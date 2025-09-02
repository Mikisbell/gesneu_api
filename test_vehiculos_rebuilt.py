#!/usr/bin/env python3
"""
Test script para verificar los endpoints reconstruidos del módulo de vehículos
"""
import asyncio
import httpx
import json
from typing import Dict, Any

# Configuración del servidor
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

class VehiculosAPITester:
    def __init__(self):
        self.base_url = f"{BASE_URL}{API_PREFIX}/vehiculos"
        self.headers = {"Content-Type": "application/json"}
        
    async def test_endpoint(self, client: httpx.AsyncClient, method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[str, Any]:
        """Prueba un endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=self.headers)
            else:
                return {"error": f"Método {method} no soportado"}
                
            return {
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content),
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200]
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "status_code": None
            }

    async def run_tests(self):
        """Ejecuta todas las pruebas de endpoints"""
        print("🚀 Iniciando pruebas de endpoints de vehículos reconstruidos...")
        print("=" * 70)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Lista de endpoints a probar
            test_cases = [
                # Endpoints principales de vehículos
                ("GET", "/", "Listar vehículos"),
                
                # Endpoints de tipos de vehículo
                ("GET", "/tipos", "Listar tipos de vehículo"),
                
                # Endpoints de configuraciones de eje
                ("GET", "/configuraciones-eje", "Listar configuraciones de eje"),
                
                # Endpoints de posiciones de neumático
                ("GET", "/posiciones-neumatico", "Listar posiciones de neumático"),
            ]
            
            results = []
            
            for method, endpoint, description in test_cases:
                print(f"\n📋 Probando: {description}")
                print(f"   {method} {self.base_url}{endpoint}")
                
                result = await self.test_endpoint(client, method, endpoint)
                result["endpoint"] = endpoint
                result["method"] = method
                result["description"] = description
                results.append(result)
                
                # Mostrar resultado
                if result["success"]:
                    status_icon = "✅"
                    status_color = "SUCCESS"
                else:
                    status_icon = "❌"
                    status_color = "FAILED"
                
                print(f"   {status_icon} Status: {result['status_code']} - {status_color}")
                
                if "error" in result:
                    print(f"   🔥 Error: {result['error']}")
                elif result["success"]:
                    if isinstance(result["data"], list):
                        print(f"   📊 Datos: Lista con {len(result['data'])} elementos")
                    elif isinstance(result["data"], dict):
                        print(f"   📊 Datos: Objeto con {len(result['data'])} campos")
                    else:
                        print(f"   📊 Datos: {str(result['data'])[:100]}...")
                
                # Pequeña pausa entre requests
                await asyncio.sleep(0.1)
            
            # Resumen final
            print("\n" + "=" * 70)
            print("📊 RESUMEN DE PRUEBAS")
            print("=" * 70)
            
            successful = sum(1 for r in results if r["success"])
            total = len(results)
            
            print(f"✅ Exitosas: {successful}/{total}")
            print(f"❌ Fallidas: {total - successful}/{total}")
            print(f"📈 Tasa de éxito: {(successful/total)*100:.1f}%")
            
            # Detalles de endpoints fallidos
            failed_tests = [r for r in results if not r["success"]]
            if failed_tests:
                print(f"\n🔥 ENDPOINTS CON PROBLEMAS:")
                for test in failed_tests:
                    print(f"   • {test['method']} {test['endpoint']} - {test['description']}")
                    if "error" in test:
                        print(f"     Error: {test['error']}")
                    else:
                        print(f"     Status: {test['status_code']}")
            
            # Verificación específica de endpoints problemáticos anteriores
            print(f"\n🎯 VERIFICACIÓN DE ENDPOINTS PROBLEMÁTICOS ANTERIORES:")
            problematic_endpoints = ["/tipos", "/configuraciones-eje", "/posiciones-neumatico"]
            
            for endpoint in problematic_endpoints:
                test_result = next((r for r in results if r["endpoint"] == endpoint), None)
                if test_result:
                    if test_result["success"]:
                        print(f"   ✅ {endpoint} - RESUELTO (Status {test_result['status_code']})")
                    else:
                        print(f"   ❌ {endpoint} - AÚN CON PROBLEMAS (Status {test_result['status_code']})")
                else:
                    print(f"   ⚠️  {endpoint} - NO PROBADO")
            
            return results

async def main():
    """Función principal"""
    tester = VehiculosAPITester()
    
    print("🔧 Verificando conectividad con el servidor...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            health_response = await client.get(f"{BASE_URL}/health")
            if health_response.status_code == 200:
                print("✅ Servidor disponible")
            else:
                print(f"⚠️  Servidor responde pero con status {health_response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return
    
    # Ejecutar pruebas
    results = await tester.run_tests()
    
    # Guardar resultados en archivo JSON
    with open("vehiculos_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultados guardados en: vehiculos_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
