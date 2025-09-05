#!/usr/bin/env python3
"""
Script de análisis de calidad de código para API GesNeu
Incluye métricas de complejidad, duplicación, cobertura y estándares
"""
import os
import subprocess
import json
import ast
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

class CodeQualityAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.source_dir = self.project_root / "ges_neu_api"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root.absolute()),
            "metrics": {},
            "issues": [],
            "recommendations": []
        }
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """Analizar complejidad ciclomática del código"""
        print("🔍 Analizando complejidad ciclomática...")
        
        complexity_results = {
            "files_analyzed": 0,
            "total_functions": 0,
            "high_complexity_functions": [],
            "average_complexity": 0,
            "max_complexity": 0
        }
        
        complexities = []
        
        for py_file in self.source_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                complexity_results["files_analyzed"] += 1
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = self._calculate_complexity(node)
                        complexities.append(complexity)
                        complexity_results["total_functions"] += 1
                        
                        if complexity > 10:  # Umbral alto de complejidad
                            complexity_results["high_complexity_functions"].append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "function": node.name,
                                "complexity": complexity,
                                "line": node.lineno
                            })
                        
                        if complexity > complexity_results["max_complexity"]:
                            complexity_results["max_complexity"] = complexity
                            
            except Exception as e:
                print(f"  ⚠️ Error analizando {py_file}: {e}")
        
        if complexities:
            complexity_results["average_complexity"] = round(sum(complexities) / len(complexities), 2)
        
        print(f"  📊 {complexity_results['files_analyzed']} archivos, {complexity_results['total_functions']} funciones")
        print(f"  📈 Complejidad promedio: {complexity_results['average_complexity']}")
        print(f"  🔺 Funciones complejas: {len(complexity_results['high_complexity_functions'])}")
        
        return complexity_results
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calcular complejidad ciclomática de un nodo AST"""
        complexity = 1  # Complejidad base
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def analyze_code_duplication(self) -> Dict[str, Any]:
        """Analizar duplicación de código"""
        print("🔄 Analizando duplicación de código...")
        
        duplication_results = {
            "files_analyzed": 0,
            "potential_duplicates": [],
            "duplicate_lines": 0,
            "duplication_percentage": 0
        }
        
        file_hashes = {}
        total_lines = 0
        
        for py_file in self.source_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                duplication_results["files_analyzed"] += 1
                total_lines += len(lines)
                
                # Analizar bloques de código similares (simplificado)
                for i in range(len(lines) - 5):  # Bloques de al menos 5 líneas
                    block = ''.join(lines[i:i+5]).strip()
                    if len(block) > 50:  # Solo bloques significativos
                        block_hash = hash(block)
                        
                        if block_hash in file_hashes:
                            duplication_results["potential_duplicates"].append({
                                "file1": file_hashes[block_hash]["file"],
                                "line1": file_hashes[block_hash]["line"],
                                "file2": str(py_file.relative_to(self.project_root)),
                                "line2": i + 1,
                                "block_size": 5
                            })
                            duplication_results["duplicate_lines"] += 5
                        else:
                            file_hashes[block_hash] = {
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": i + 1
                            }
                            
            except Exception as e:
                print(f"  ⚠️ Error analizando {py_file}: {e}")
        
        if total_lines > 0:
            duplication_results["duplication_percentage"] = round(
                (duplication_results["duplicate_lines"] / total_lines) * 100, 2
            )
        
        print(f"  📊 {duplication_results['files_analyzed']} archivos analizados")
        print(f"  🔄 {len(duplication_results['potential_duplicates'])} duplicaciones potenciales")
        print(f"  📈 {duplication_results['duplication_percentage']}% duplicación estimada")
        
        return duplication_results
    
    def analyze_imports_and_dependencies(self) -> Dict[str, Any]:
        """Analizar imports y dependencias"""
        print("📦 Analizando imports y dependencias...")
        
        import_results = {
            "files_analyzed": 0,
            "total_imports": 0,
            "unused_imports": [],
            "circular_imports": [],
            "external_dependencies": set(),
            "internal_imports": set()
        }
        
        for py_file in self.source_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                import_results["files_analyzed"] += 1
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_results["total_imports"] += 1
                            if alias.name.startswith("ges_neu_api"):
                                import_results["internal_imports"].add(alias.name)
                            else:
                                import_results["external_dependencies"].add(alias.name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            import_results["total_imports"] += 1
                            if node.module.startswith("ges_neu_api"):
                                import_results["internal_imports"].add(node.module)
                            else:
                                import_results["external_dependencies"].add(node.module)
                            
            except Exception as e:
                print(f"  ⚠️ Error analizando {py_file}: {e}")
        
        # Convertir sets a listas para JSON
        import_results["external_dependencies"] = list(import_results["external_dependencies"])
        import_results["internal_imports"] = list(import_results["internal_imports"])
        
        print(f"  📊 {import_results['files_analyzed']} archivos, {import_results['total_imports']} imports")
        print(f"  📦 {len(import_results['external_dependencies'])} dependencias externas")
        print(f"  🏠 {len(import_results['internal_imports'])} imports internos")
        
        return import_results
    
    def analyze_code_style(self) -> Dict[str, Any]:
        """Analizar estilo de código con ruff"""
        print("🎨 Analizando estilo de código...")
        
        style_results = {
            "tool": "ruff",
            "files_checked": 0,
            "issues_found": 0,
            "issues_by_category": {},
            "issues_details": []
        }
        
        try:
            # Ejecutar ruff check
            result = subprocess.run(
                ["ruff", "check", str(self.source_dir), "--output-format=json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                style_results["issues_found"] = len(issues)
                
                for issue in issues:
                    category = issue.get("code", "unknown")
                    if category not in style_results["issues_by_category"]:
                        style_results["issues_by_category"][category] = 0
                    style_results["issues_by_category"][category] += 1
                    
                    style_results["issues_details"].append({
                        "file": issue.get("filename", ""),
                        "line": issue.get("location", {}).get("row", 0),
                        "column": issue.get("location", {}).get("column", 0),
                        "code": issue.get("code", ""),
                        "message": issue.get("message", ""),
                        "severity": "error" if issue.get("code", "").startswith("E") else "warning"
                    })
            
            print(f"  📊 {style_results['issues_found']} issues encontrados")
            for category, count in style_results["issues_by_category"].items():
                print(f"    {category}: {count}")
                
        except FileNotFoundError:
            print("  ⚠️ ruff no encontrado, instalando...")
            subprocess.run([sys.executable, "-m", "pip", "install", "ruff"])
            return self.analyze_code_style()
        except Exception as e:
            print(f"  ❌ Error ejecutando ruff: {e}")
            style_results["error"] = str(e)
        
        return style_results
    
    def analyze_type_hints(self) -> Dict[str, Any]:
        """Analizar uso de type hints"""
        print("🏷️ Analizando type hints...")
        
        type_results = {
            "files_analyzed": 0,
            "total_functions": 0,
            "functions_with_hints": 0,
            "functions_without_hints": [],
            "coverage_percentage": 0
        }
        
        for py_file in self.source_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                type_results["files_analyzed"] += 1
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        type_results["total_functions"] += 1
                        
                        has_hints = (
                            node.returns is not None or
                            any(arg.annotation is not None for arg in node.args.args)
                        )
                        
                        if has_hints:
                            type_results["functions_with_hints"] += 1
                        else:
                            type_results["functions_without_hints"].append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "function": node.name,
                                "line": node.lineno
                            })
                            
            except Exception as e:
                print(f"  ⚠️ Error analizando {py_file}: {e}")
        
        if type_results["total_functions"] > 0:
            type_results["coverage_percentage"] = round(
                (type_results["functions_with_hints"] / type_results["total_functions"]) * 100, 2
            )
        
        print(f"  📊 {type_results['total_functions']} funciones analizadas")
        print(f"  🏷️ {type_results['coverage_percentage']}% con type hints")
        
        return type_results
    
    def generate_recommendations(self):
        """Generar recomendaciones basadas en el análisis"""
        complexity = self.results["metrics"].get("complexity", {})
        duplication = self.results["metrics"].get("duplication", {})
        style = self.results["metrics"].get("style", {})
        type_hints = self.results["metrics"].get("type_hints", {})
        
        recommendations = []
        
        # Recomendaciones de complejidad
        if complexity.get("average_complexity", 0) > 5:
            recommendations.append("Reducir complejidad promedio de funciones (objetivo: <5)")
        
        if len(complexity.get("high_complexity_functions", [])) > 0:
            recommendations.append(f"Refactorizar {len(complexity['high_complexity_functions'])} funciones con alta complejidad")
        
        # Recomendaciones de duplicación
        if duplication.get("duplication_percentage", 0) > 5:
            recommendations.append("Reducir duplicación de código (objetivo: <5%)")
        
        # Recomendaciones de estilo
        if style.get("issues_found", 0) > 0:
            recommendations.append(f"Corregir {style['issues_found']} issues de estilo de código")
        
        # Recomendaciones de type hints
        if type_hints.get("coverage_percentage", 0) < 80:
            recommendations.append("Mejorar cobertura de type hints (objetivo: >80%)")
        
        self.results["recommendations"] = recommendations
    
    def run_full_analysis(self):
        """Ejecutar análisis completo de calidad de código"""
        print("🔍 INICIANDO ANÁLISIS DE CALIDAD DE CÓDIGO")
        print("=" * 50)
        
        # Ejecutar todos los análisis
        self.results["metrics"]["complexity"] = self.analyze_complexity()
        self.results["metrics"]["duplication"] = self.analyze_code_duplication()
        self.results["metrics"]["imports"] = self.analyze_imports_and_dependencies()
        self.results["metrics"]["style"] = self.analyze_code_style()
        self.results["metrics"]["type_hints"] = self.analyze_type_hints()
        
        # Generar recomendaciones
        self.generate_recommendations()
        
        # Guardar reporte
        self.save_report()
        
        # Mostrar resumen
        self.show_summary()
    
    def save_report(self):
        """Guardar reporte de calidad de código"""
        filename = f"code_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(self.project_root / filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado en: {filename}")
    
    def show_summary(self):
        """Mostrar resumen del análisis"""
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE CALIDAD DE CÓDIGO")
        print("=" * 50)
        
        metrics = self.results["metrics"]
        
        # Complejidad
        complexity = metrics.get("complexity", {})
        print(f"🔍 Complejidad:")
        print(f"  • Promedio: {complexity.get('average_complexity', 0)}")
        print(f"  • Funciones complejas: {len(complexity.get('high_complexity_functions', []))}")
        
        # Duplicación
        duplication = metrics.get("duplication", {})
        print(f"🔄 Duplicación:")
        print(f"  • Porcentaje: {duplication.get('duplication_percentage', 0)}%")
        print(f"  • Duplicaciones: {len(duplication.get('potential_duplicates', []))}")
        
        # Estilo
        style = metrics.get("style", {})
        print(f"🎨 Estilo:")
        print(f"  • Issues: {style.get('issues_found', 0)}")
        
        # Type hints
        type_hints = metrics.get("type_hints", {})
        print(f"🏷️ Type Hints:")
        print(f"  • Cobertura: {type_hints.get('coverage_percentage', 0)}%")
        
        # Recomendaciones
        if self.results["recommendations"]:
            print(f"\n💡 Recomendaciones:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        # Score general
        score = self.calculate_quality_score()
        print(f"\n🎯 Score de Calidad: {score}/100")
        
        if score >= 80:
            print("🎉 EXCELENTE - Código de alta calidad")
        elif score >= 60:
            print("⚠️ BUENO - Algunas mejoras recomendadas")
        else:
            print("❌ CRÍTICO - Requiere mejoras significativas")
    
    def calculate_quality_score(self) -> int:
        """Calcular score general de calidad"""
        metrics = self.results["metrics"]
        
        score = 100
        
        # Penalizar complejidad alta
        complexity = metrics.get("complexity", {})
        avg_complexity = complexity.get("average_complexity", 0)
        if avg_complexity > 5:
            score -= min(20, (avg_complexity - 5) * 4)
        
        # Penalizar duplicación
        duplication = metrics.get("duplication", {})
        dup_percentage = duplication.get("duplication_percentage", 0)
        if dup_percentage > 5:
            score -= min(15, (dup_percentage - 5) * 2)
        
        # Penalizar issues de estilo
        style = metrics.get("style", {})
        issues = style.get("issues_found", 0)
        score -= min(25, issues * 0.5)
        
        # Penalizar falta de type hints
        type_hints = metrics.get("type_hints", {})
        coverage = type_hints.get("coverage_percentage", 0)
        if coverage < 80:
            score -= min(20, (80 - coverage) * 0.5)
        
        return max(0, int(score))

if __name__ == "__main__":
    analyzer = CodeQualityAnalyzer()
    analyzer.run_full_analysis()
