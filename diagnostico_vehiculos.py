#!/usr/bin/env python3
"""
Diagnóstico específico para identificar el error 500 en módulo vehículos
"""
import sys
import traceback

def diagnosticar_importaciones():
    """Verifica si hay problemas en las importaciones del módulo vehículos"""
    print("=== DIAGNÓSTICO DE IMPORTACIONES VEHÍCULOS ===")
    
    try:
        print("1. Importando modelos de vehículos...")
        from ges_neu_api.modules.vehiculos.models import Vehiculos, TiposVehiculo, ConfiguracionesEje
        print("✅ Modelos importados correctamente")
        
        print("2. Importando servicio de vehículos...")
        from ges_neu_api.modules.vehiculos.service import VehiculosService
        print("✅ Servicio importado correctamente")
        
        print("3. Importando dependencias de vehículos...")
        from ges_neu_api.modules.vehiculos.dependencies import get_vehiculos_service
        print("✅ Dependencias importadas correctamente")
        
        print("4. Importando router de vehículos...")
        from ges_neu_api.modules.vehiculos.router import router
        print("✅ Router importado correctamente")
        
        print("5. Verificando schemas...")
        from ges_neu_api.modules.vehiculos.schemas import VehiculoRead, VehiculoCreate
        print("✅ Schemas importados correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def verificar_modelos_sqlalchemy():
    """Verifica si los modelos SQLAlchemy están bien definidos"""
    print("\n=== VERIFICACIÓN DE MODELOS SQLALCHEMY ===")
    
    try:
        from ges_neu_api.modules.vehiculos.models import Vehiculos, TiposVehiculo
        
        print("1. Verificando tabla Vehiculos...")
        print(f"   Nombre tabla: {Vehiculos.__tablename__}")
        print(f"   Campos: {list(Vehiculos.__fields__.keys())}")
        
        print("2. Verificando tabla TiposVehiculo...")
        print(f"   Nombre tabla: {TiposVehiculo.__tablename__}")
        print(f"   Campos: {list(TiposVehiculo.__fields__.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def probar_instanciacion_servicio():
    """Prueba crear una instancia del servicio de vehículos"""
    print("\n=== PRUEBA DE INSTANCIACIÓN DE SERVICIO ===")
    
    try:
        from unittest.mock import Mock
        from ges_neu_api.modules.vehiculos.service import VehiculosService
        
        # Mock de sesión async
        mock_session = Mock()
        servicio = VehiculosService(mock_session)
        print("✅ Servicio VehiculosService instanciado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error instanciando servicio: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("DIAGNÓSTICO COMPLETO DEL MÓDULO VEHÍCULOS\n")
    
    resultados = []
    resultados.append(diagnosticar_importaciones())
    resultados.append(verificar_modelos_sqlalchemy())
    resultados.append(probar_instanciacion_servicio())
    
    exitosos = sum(resultados)
    total = len(resultados)
    
    print(f"\n=== RESUMEN DIAGNÓSTICO ===")
    print(f"Pruebas exitosas: {exitosos}/{total}")
    
    if exitosos == total:
        print("✅ Módulo vehículos parece estar correcto a nivel de código")
        print("   El error 500 puede ser de conexión BD o datos específicos")
    else:
        print("❌ Hay problemas en el módulo vehículos que requieren corrección")
