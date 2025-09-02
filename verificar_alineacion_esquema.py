#!/usr/bin/env python3
"""
Script para verificar alineación de modelos con ESQUEMA_COMPLETO_BD.md
y probar todos los endpoints después de las correcciones
"""
import requests
import json
from typing import Dict, Any

# Token JWT válido
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc4MDM5MH0.mjWUaVDnmznHp_a4m2zfshDquv0XRuZFqR-FGReaDQE"
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def probar_endpoint(endpoint: str, nombre: str) -> Dict[str, Any]:
    """Prueba un endpoint y devuelve información detallada"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=10)
        
        resultado = {
            "nombre": nombre,
            "endpoint": endpoint,
            "status": response.status_code,
            "exitoso": response.status_code == 200
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    resultado["elementos"] = len(data)
                    if data:
                        resultado["primer_elemento"] = data[0]
                else:
                    resultado["tipo_respuesta"] = type(data).__name__
            except:
                resultado["respuesta"] = "No JSON"
        else:
            resultado["error"] = response.text[:200] if response.text else "Sin detalles"
            
        return resultado
        
    except requests.exceptions.RequestException as e:
        return {
            "nombre": nombre,
            "endpoint": endpoint,
            "status": "ERROR_CONEXION",
            "exitoso": False,
            "error": str(e)
        }

def main():
    print("=== VERIFICACIÓN DE ALINEACIÓN CON ESQUEMA_COMPLETO_BD.md ===\n")
    
    # Lista de endpoints a probar según el esquema
    endpoints_prueba = [
        # Módulo Catálogos (ya funcionando)
        ("/catalogos/proveedores", "Proveedores"),
        ("/catalogos/almacenes", "Almacenes"), 
        ("/catalogos/motivos-desecho", "Motivos Desecho"),
        ("/catalogos/parametros-inventario", "Parámetros Inventario"),
        
        # Módulo Neumáticos (corregido)
        ("/neumaticos/", "Neumáticos"),
        ("/neumaticos/fabricantes", "Fabricantes Neumático"),
        ("/neumaticos/modelos", "Modelos Neumático"),
        
        # Módulo Vehículos (a verificar)
        ("/vehiculos/", "Vehículos"),
        ("/vehiculos/tipos", "Tipos Vehículo"),
        ("/vehiculos/configuraciones-eje", "Configuraciones Eje"),
        
        # Módulo Auth
        ("/auth/me", "Usuario Actual"),
        
        # Salud del sistema
        ("/health", "Health Check"),
    ]
    
    resultados = []
    exitosos = 0
    
    for endpoint, nombre in endpoints_prueba:
        print(f"Probando {nombre}...")
        resultado = probar_endpoint(endpoint, nombre)
        resultados.append(resultado)
        
        if resultado["exitoso"]:
            exitosos += 1
            elementos = resultado.get("elementos", "N/A")
            print(f"✅ {nombre}: Status {resultado['status']} - {elementos} elementos")
        else:
            print(f"❌ {nombre}: Status {resultado['status']}")
            if "error" in resultado:
                print(f"   Error: {resultado['error'][:100]}...")
    
    print(f"\n=== RESUMEN FINAL ===")
    print(f"Endpoints exitosos: {exitosos}/{len(endpoints_prueba)}")
    print(f"Porcentaje de éxito: {(exitosos/len(endpoints_prueba)*100):.1f}%")
    
    # Mostrar detalles de errores
    errores = [r for r in resultados if not r["exitoso"]]
    if errores:
        print(f"\n=== ENDPOINTS CON ERRORES ===")
        for error in errores:
            print(f"❌ {error['nombre']} ({error['endpoint']}): {error['status']}")
            if "error" in error:
                print(f"   Detalle: {error['error'][:150]}...")
    
    # Guardar resultados detallados
    with open("resultados_verificacion.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nResultados detallados guardados en: resultados_verificacion.json")

if __name__ == "__main__":
    main()
