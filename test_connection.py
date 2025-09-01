#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos y funcionalidad básica.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ges_neu_api.core.config import settings
from ges_neu_api.core.database import sync_engine, SyncSessionLocal
from sqlalchemy import text

def test_database_connection():
    """Prueba la conexión básica a la base de datos"""
    print("=== PRUEBA DE CONEXIÓN A BASE DE DATOS ===")
    print(f"URL de conexión: {settings.SQLALCHEMY_DATABASE_URI}")
    
    try:
        # Probar conexión directa con el engine
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("OK - Conexion exitosa a PostgreSQL")
            print(f"  Version: {version}")
            
            # Probar consulta a una tabla existente
            result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
            count = result.fetchone()[0]
            print(f"OK - Tabla 'usuarios' accesible - Registros: {count}")
            
            # Probar otras tablas principales
            tables_to_test = ['vehiculos', 'neumaticos', 'roles', 'permisos']
            for table in tables_to_test:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"OK - Tabla '{table}' accesible - Registros: {count}")
                except Exception as e:
                    print(f"ERROR - Tabla '{table}' - Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR - Error de conexion: {e}")
        return False

def test_session():
    """Prueba la creación de sesiones"""
    print("\n=== PRUEBA DE SESIONES ===")
    
    try:
        db = SyncSessionLocal()
        result = db.execute(text("SELECT 1"))
        value = result.fetchone()[0]
        db.close()
        
        if value == 1:
            print("OK - Sesion de base de datos funciona correctamente")
            return True
        else:
            print("ERROR - Error en sesion de base de datos")
            return False
            
    except Exception as e:
        print(f"ERROR - Error en sesion: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("Iniciando pruebas de conexion...\n")
    
    # Prueba 1: Conexión a base de datos
    db_ok = test_database_connection()
    
    # Prueba 2: Sesiones
    session_ok = test_session()
    
    # Resumen
    print("\n=== RESUMEN ===")
    print(f"Conexion a BD: {'OK' if db_ok else 'FALLO'}")
    print(f"Sesiones:      {'OK' if session_ok else 'FALLO'}")
    
    if db_ok and session_ok:
        print("\nTodas las pruebas pasaron! La API esta lista para usar.")
        return 0
    else:
        print("\nAlgunas pruebas fallaron. Revisa la configuracion.")
        return 1

if __name__ == "__main__":
    exit(main())
