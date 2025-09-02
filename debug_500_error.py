#!/usr/bin/env python3
"""
Script para diagnosticar el error 500 en configuraciones-eje
"""
import asyncio
import sys
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from ges_neu_api.core.database import get_session
from ges_neu_api.modules.vehiculos.service import VehiculosService

async def test_configuraciones_eje():
    """Test directo del servicio configuraciones-eje"""
    print("=== DIAGNÓSTICO ERROR 500 CONFIGURACIONES-EJE ===")
    
    try:
        # Obtener sesión de BD
        print("1. Obteniendo sesión de base de datos...")
        async for session in get_session():
            print("   ✓ Sesión obtenida correctamente")
            
            # Crear instancia del servicio
            print("2. Creando instancia del servicio...")
            service = VehiculosService(session)
            print("   ✓ Servicio creado correctamente")
            
            # Intentar ejecutar get_multi_configuraciones_eje
            print("3. Ejecutando get_multi_configuraciones_eje...")
            try:
                result = await service.get_multi_configuraciones_eje()
                print(f"   ✓ Resultado obtenido: {len(result) if result else 0} registros")
                if result:
                    print(f"   ✓ Primer registro: {result[0]}")
                else:
                    print("   ⚠ No hay registros en la tabla")
                    
            except Exception as service_error:
                print(f"   ❌ Error en servicio: {type(service_error).__name__}: {service_error}")
                print(f"   📋 Traceback completo:")
                traceback.print_exc()
                
            break  # Solo necesitamos una iteración
            
    except Exception as db_error:
        print(f"❌ Error de base de datos: {type(db_error).__name__}: {db_error}")
        print(f"📋 Traceback completo:")
        traceback.print_exc()

async def test_http_endpoint():
    """Test HTTP directo al endpoint"""
    import httpx
    
    print("\n=== TEST HTTP ENDPOINT ===")
    
    try:
        async with httpx.AsyncClient() as client:
            print("4. Realizando petición HTTP GET...")
            response = await client.get("http://localhost:8000/api/v1/vehiculos/configuraciones-eje")
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 500:
                print("   ❌ Error 500 confirmado")
                try:
                    error_detail = response.json()
                    print(f"   📋 Detalle del error: {error_detail}")
                except:
                    print(f"   📋 Respuesta raw: {response.text}")
            else:
                print(f"   ✓ Respuesta exitosa: {response.json()}")
                
    except Exception as http_error:
        print(f"❌ Error HTTP: {type(http_error).__name__}: {http_error}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Iniciando diagnóstico completo...")
    
    # Test del servicio
    asyncio.run(test_configuraciones_eje())
    
    # Test HTTP
    asyncio.run(test_http_endpoint())
    
    print("\n=== DIAGNÓSTICO COMPLETADO ===")
