#!/usr/bin/env python3
"""
Script maestro para ejecutar todas las suites de pruebas de API GesNeu
Incluye tests básicos, avanzados, performance, seguridad e integración
"""
import asyncio
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import time

class MasterTestRunner:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {},
            "recommendations": []
        }
    
    def run_basic_api_tests(self) -> Dict[str, Any]:
        """Ejecutar tests básicos de API"""
        print("🚀 Ejecutando tests básicos de API...")
        
        try:
            # Ejecutar el script de tests completos
            result = subprocess.run([
                sys.executable, "test_completo_api.py"
            ], capture_output=True, text=True, cwd=self.project_root, timeout=300)
            
            basic_results = {
                "status": "success" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "duration_seconds": 0,  # Se calculará en el script real
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Intentar parsear resultados JSON si existen
            try:
                # Buscar archivos de resultados recientes
                result_files = list(self.project_root.glob("test_results_*.json"))
                if result_files:
                    latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        test_data = json.load(f)
                        basic_results["detailed_results"] = test_data
            except Exception:
                pass
            
            print(f"  ✅ Tests básicos: {'EXITOSO' if basic_results['status'] == 'success' else 'FALLÓ'}")
            return basic_results
            
        except subprocess.TimeoutExpired:
            print("  ⏰ Tests básicos: TIMEOUT")
            return {"status": "timeout", "error": "Tests básicos excedieron tiempo límite"}
        except Exception as e:
            print(f"  ❌ Tests básicos: ERROR - {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de performance"""
        print("⚡ Ejecutando tests de performance...")
        
        try:
            # Importar y ejecutar suite de performance
            sys.path.append(str(self.project_root / "tests" / "advanced"))
            from test_performance import PerformanceTestSuite
            
            suite = PerformanceTestSuite()
            await suite.run_full_performance_suite()
            
            perf_results = {
                "status": "success",
                "results": suite.results
            }
            
            print("  ✅ Tests de performance: COMPLETADOS")
            return perf_results
            
        except Exception as e:
            print(f"  ❌ Tests de performance: ERROR - {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_security_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de seguridad"""
        print("🛡️ Ejecutando tests de seguridad...")
        
        try:
            # Importar y ejecutar suite de seguridad
            sys.path.append(str(self.project_root / "tests" / "advanced"))
            from test_security import SecurityTestSuite
            
            suite = SecurityTestSuite()
            await suite.run_full_security_suite()
            
            security_results = {
                "status": "success",
                "results": suite.results
            }
            
            print("  ✅ Tests de seguridad: COMPLETADOS")
            return security_results
            
        except Exception as e:
            print(f"  ❌ Tests de seguridad: ERROR - {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de integración"""
        print("🔗 Ejecutando tests de integración...")
        
        try:
            # Importar y ejecutar suite de integración
            sys.path.append(str(self.project_root / "tests" / "advanced"))
            from test_integration import IntegrationTestSuite
            
            suite = IntegrationTestSuite()
            await suite.run_full_integration_suite()
            
            integration_results = {
                "status": "success",
                "results": suite.results
            }
            
            print("  ✅ Tests de integración: COMPLETADOS")
            return integration_results
            
        except Exception as e:
            print(f"  ❌ Tests de integración: ERROR - {e}")
            return {"status": "error", "error": str(e)}
    
    def run_code_quality_analysis(self) -> Dict[str, Any]:
        """Ejecutar análisis de calidad de código"""
        print("🔍 Ejecutando análisis de calidad de código...")
        
        try:
            # Ejecutar script de análisis de calidad
            result = subprocess.run([
                sys.executable, "scripts/code_quality_check.py"
            ], capture_output=True, text=True, cwd=self.project_root, timeout=300)
            
            quality_results = {
                "status": "success" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Intentar parsear resultados JSON
            try:
                result_files = list(self.project_root.glob("code_quality_report_*.json"))
                if result_files:
                    latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        quality_data = json.load(f)
                        quality_results["detailed_results"] = quality_data
            except Exception:
                pass
            
            print(f"  ✅ Análisis de calidad: {'COMPLETADO' if quality_results['status'] == 'success' else 'FALLÓ'}")
            return quality_results
            
        except Exception as e:
            print(f"  ❌ Análisis de calidad: ERROR - {e}")
            return {"status": "error", "error": str(e)}
    
    def run_pytest_suite(self) -> Dict[str, Any]:
        """Ejecutar suite completa de pytest"""
        print("🧪 Ejecutando suite de pytest...")
        
        try:
            # Ejecutar pytest con cobertura
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/", 
                "-v", 
                "--cov=ges_neu_api", 
                "--cov-report=term-missing",
                "--cov-report=json"
            ], capture_output=True, text=True, cwd=self.project_root, timeout=600)
            
            pytest_results = {
                "status": "success" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Intentar parsear cobertura
            try:
                coverage_file = self.project_root / "coverage.json"
                if coverage_file.exists():
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                        pytest_results["coverage"] = {
                            "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                            "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                            "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0)
                        }
            except Exception:
                pass
            
            print(f"  ✅ Pytest: {'EXITOSO' if pytest_results['status'] == 'success' else 'FALLÓ'}")
            return pytest_results
            
        except subprocess.TimeoutExpired:
            print("  ⏰ Pytest: TIMEOUT")
            return {"status": "timeout", "error": "Pytest excedió tiempo límite"}
        except Exception as e:
            print(f"  ❌ Pytest: ERROR - {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_all_test_suites(self):
        """Ejecutar todas las suites de pruebas"""
        print("🏁 INICIANDO SUITE COMPLETA DE PRUEBAS")
        print("=" * 60)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        start_time = time.time()
        
        # Ejecutar todas las suites
        self.results["test_suites"]["basic_api"] = self.run_basic_api_tests()
        self.results["test_suites"]["pytest"] = self.run_pytest_suite()
        self.results["test_suites"]["performance"] = await self.run_performance_tests()
        self.results["test_suites"]["security"] = await self.run_security_tests()
        self.results["test_suites"]["integration"] = await self.run_integration_tests()
        self.results["test_suites"]["code_quality"] = self.run_code_quality_analysis()
        
        total_time = time.time() - start_time
        
        # Generar resumen
        self.generate_summary(total_time)
        
        # Guardar reporte maestro
        self.save_master_report()
        
        # Mostrar resultados finales
        self.show_final_results()
    
    def generate_summary(self, total_time: float):
        """Generar resumen de todas las pruebas"""
        suites = self.results["test_suites"]
        
        successful_suites = sum(1 for suite in suites.values() if suite.get("status") == "success")
        total_suites = len(suites)
        
        self.results["summary"] = {
            "total_suites": total_suites,
            "successful_suites": successful_suites,
            "failed_suites": total_suites - successful_suites,
            "success_rate": round((successful_suites / total_suites * 100) if total_suites > 0 else 0, 2),
            "total_duration_seconds": round(total_time, 2)
        }
        
        # Generar recomendaciones
        recommendations = []
        
        if suites.get("basic_api", {}).get("status") != "success":
            recommendations.append("Corregir tests básicos de API antes de continuar")
        
        if suites.get("security", {}).get("status") == "success":
            security_results = suites["security"].get("results", {})
            if security_results.get("summary", {}).get("security_score", 0) < 80:
                recommendations.append("Mejorar score de seguridad (objetivo: >80%)")
        
        if suites.get("code_quality", {}).get("status") == "success":
            quality_results = suites["code_quality"].get("detailed_results", {})
            if quality_results.get("recommendations"):
                recommendations.extend(quality_results["recommendations"][:3])  # Top 3
        
        self.results["recommendations"] = recommendations
    
    def save_master_report(self):
        """Guardar reporte maestro"""
        filename = f"master_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(self.project_root / filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte maestro guardado en: {filename}")
    
    def show_final_results(self):
        """Mostrar resultados finales"""
        print("\n" + "=" * 60)
        print("🏆 RESULTADOS FINALES DE TODAS LAS PRUEBAS")
        print("=" * 60)
        
        summary = self.results["summary"]
        
        print(f"📊 Suites ejecutadas: {summary['total_suites']}")
        print(f"✅ Exitosas: {summary['successful_suites']}")
        print(f"❌ Fallidas: {summary['failed_suites']}")
        print(f"📈 Tasa de éxito: {summary['success_rate']}%")
        print(f"⏱️ Tiempo total: {summary['total_duration_seconds']}s")
        
        # Mostrar estado de cada suite
        print(f"\n📋 Detalle por suite:")
        for suite_name, suite_data in self.results["test_suites"].items():
            status = suite_data.get("status", "unknown")
            icon = "✅" if status == "success" else "❌" if status == "failed" else "⏰" if status == "timeout" else "❓"
            print(f"  {icon} {suite_name.replace('_', ' ').title()}: {status.upper()}")
        
        # Mostrar recomendaciones
        if self.results["recommendations"]:
            print(f"\n💡 Recomendaciones principales:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        # Evaluación general
        print(f"\n🎯 EVALUACIÓN GENERAL:")
        if summary["success_rate"] >= 90:
            print("🎉 EXCELENTE - API lista para producción")
        elif summary["success_rate"] >= 70:
            print("⚠️ BUENO - Algunas mejoras recomendadas")
        elif summary["success_rate"] >= 50:
            print("🔧 REGULAR - Requiere correcciones importantes")
        else:
            print("❌ CRÍTICO - Requiere atención inmediata")

async def main():
    """Función principal"""
    runner = MasterTestRunner()
    await runner.run_all_test_suites()

if __name__ == "__main__":
    asyncio.run(main())
