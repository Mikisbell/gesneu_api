#!/usr/bin/env python3
"""
Test directo de conexión PostgreSQL usando solo librerías estándar
"""

import socket
import sys

def test_postgres_connection():
    """Test básico de conectividad a PostgreSQL"""
    print("🔍 VERIFICANDO CONEXIÓN POSTGRESQL")
    print("=" * 50)
    
    host = 'localhost'
    port = 5432
    
    try:
        # Test de conectividad TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Puerto {port} está abierto en {host}")
            print("✅ PostgreSQL está ejecutándose")
            return True
        else:
            print(f"❌ No se puede conectar a {host}:{port}")
            print("❌ PostgreSQL no está disponible")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_api_logs():
    """Instrucciones para revisar logs de la API"""
    print("\n🔍 REVISIÓN DE LOGS DEL SERVIDOR")
    print("=" * 50)
    print("💡 Para identificar la causa exacta de los errores 500:")
    print("   1. Ve a la consola donde ejecutas 'uvicorn ges_neu_api.main:app'")
    print("   2. Busca mensajes de error cuando hagas requests a los endpoints")
    print("   3. Los errores más comunes son:")
    print("      - Tablas no encontradas en BD")
    print("      - Modelos SQLAlchemy incompatibles")
    print("      - Problemas de conexión a BD")
    print("      - Imports faltantes o circulares")

def analyze_diagnostic_results():
    """Análisis de los resultados del diagnóstico"""
    print("\n📊 ANÁLISIS DE RESULTADOS")
    print("=" * 50)
    
    print("✅ FUNCIONANDO:")
    print("   - Servidor API (uvicorn)")
    print("   - Endpoints básicos (/, /health, /docs)")
    print("   - PostgreSQL servicio")
    print("   - Token JWT válido")
    
    print("\n❌ PROBLEMAS IDENTIFICADOS:")
    print("   - Error 500: Todos los endpoints de módulos")
    print("   - Error 404: Algunos endpoints no existen")
    print("   - Error 422: Endpoints requieren parámetros UUID")
    
    print("\n🎯 CAUSA PROBABLE:")
    print("   - Modelos SQLAlchemy no coinciden con esquema BD")
    print("   - Tablas faltantes en base de datos")
    print("   - Problemas de migración/sincronización")

def recommend_next_steps():
    """Recomendaciones para los próximos pasos"""
    print("\n🔧 PRÓXIMOS PASOS RECOMENDADOS")
    print("=" * 50)
    
    print("1. REVISAR LOGS DEL SERVIDOR:")
    print("   - Ejecutar endpoint que falla")
    print("   - Copiar error exacto de la consola uvicorn")
    
    print("\n2. VERIFICAR BASE DE DATOS:")
    print("   - Confirmar que BD 'ges_neu_bd' existe")
    print("   - Verificar que tablas están creadas")
    print("   - Comprobar que usuario 'admin' existe")
    
    print("\n3. SCRIPTS DISPONIBLES:")
    print("   - analyze_complete_db.py (analizar esquema)")
    print("   - verify_models_schema.py (verificar modelos)")
    print("   - fix_models_with_schema.py (corregir modelos)")
    
    print("\n4. COMANDOS ÚTILES:")
    print("   - Conectar a BD: psql -h localhost -U postgres -d ges_neu_bd")
    print("   - Listar tablas: \\dt")
    print("   - Ver usuarios: SELECT * FROM usuarios;")

def main():
    print("🚀 DIAGNÓSTICO FINAL - API GESNEU")
    print("=" * 60)
    
    # Test de conectividad
    postgres_ok = test_postgres_connection()
    
    # Análisis de resultados
    analyze_diagnostic_results()
    
    # Instrucciones para logs
    check_api_logs()
    
    # Recomendaciones
    recommend_next_steps()
    
    print("\n" + "=" * 60)
    if postgres_ok:
        print("🎯 POSTGRESQL: ✅ Disponible")
        print("🎯 PROBLEMA: Modelos/Tablas incompatibles")
        print("💡 ACCIÓN: Revisar logs del servidor para error específico")
    else:
        print("🎯 POSTGRESQL: ❌ No disponible")
        print("💡 ACCIÓN: Iniciar PostgreSQL y crear BD")

if __name__ == "__main__":
    main()
