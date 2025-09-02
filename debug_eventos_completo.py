#!/usr/bin/env python3
"""
Diagnóstico completo del módulo eventos para identificar causa exacta del error 500.
"""
import sys
import os
import asyncio
import traceback

sys.path.insert(0, os.path.abspath('.'))

async def test_database_connection():
    """Verificar conexión a BD y existencia de tabla eventos_neumaticos."""
    try:
        from ges_neu_api.core.database import engine
        
        print("🔍 Verificando conexión a BD...")
        
        async with engine.begin() as conn:
            # Verificar si tabla existe
            result = await conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'eventos_neumaticos'"
            )
            table_exists = result.scalar() > 0
            print(f"Tabla eventos_neumaticos existe: {table_exists}")
            
            if table_exists:
                # Verificar estructura de tabla
                result = await conn.execute(
                    "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'eventos_neumaticos' ORDER BY ordinal_position"
                )
                columns = result.fetchall()
                print(f"Columnas en tabla ({len(columns)}):")
                for col in columns[:10]:  # Primeras 10 columnas
                    print(f"  - {col[0]}: {col[1]}")
                
                # Verificar si hay datos
                result = await conn.execute("SELECT COUNT(*) FROM eventos_neumaticos")
                count = result.scalar()
                print(f"Registros en tabla: {count}")
            
            return table_exists
            
    except Exception as e:
        print(f"❌ Error BD: {str(e)}")
        traceback.print_exc()
        return False

async def test_model_import():
    """Probar import del modelo EventosNeumaticos."""
    try:
        print("\n🔍 Probando import del modelo...")
        
        from ges_neu_api.modules.eventos.models import EventosNeumaticos, TipoEventoNeumaticoEnum
        print("✅ Modelo EventosNeumaticos importado")
        
        # Verificar campos del modelo
        fields = EventosNeumaticos.__fields__
        print(f"Campos del modelo ({len(fields)}):")
        for field_name in list(fields.keys())[:10]:  # Primeros 10 campos
            print(f"  - {field_name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error import modelo: {str(e)}")
        traceback.print_exc()
        return False

async def test_service_direct():
    """Probar servicio de eventos directamente."""
    try:
        print("\n🔍 Probando EventosService directamente...")
        
        from ges_neu_api.core.database import get_session
        from ges_neu_api.modules.eventos.service import EventosService
        
        async for db in get_session():
            service = EventosService(db)
            
            # Test simple query
            eventos = await service.get_eventos(skip=0, limit=1)
            print(f"✅ get_eventos exitoso: {len(eventos)} eventos")
            
            break
            
        return True
        
    except Exception as e:
        print(f"❌ Error servicio: {str(e)}")
        traceback.print_exc()
        return False

async def test_router_import():
    """Probar import del router de eventos."""
    try:
        print("\n🔍 Probando import del router...")
        
        from ges_neu_api.modules.eventos.router import router
        print("✅ Router eventos importado")
        
        # Verificar rutas
        routes = router.routes
        print(f"Rutas definidas ({len(routes)}):")
        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  - {list(route.methods)[0] if route.methods else 'N/A'} {route.path}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error import router: {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """Ejecutar todos los tests de diagnóstico."""
    print("🚀 Iniciando diagnóstico completo del módulo Eventos...\n")
    
    tests = [
        ("Conexión BD", test_database_connection),
        ("Import Modelo", test_model_import),
        ("Import Router", test_router_import),
        ("Servicio Directo", test_service_direct),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} falló: {str(e)}")
            results[test_name] = False
    
    print(f"\n📊 Resumen de diagnóstico:")
    for test_name, success in results.items():
        status = "✅ EXITOSO" if success else "❌ FALLÓ"
        print(f"  - {test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\n🎯 Resultado final: {'✅ TODOS LOS TESTS PASARON' if all_passed else '❌ ALGUNOS TESTS FALLARON'}")

if __name__ == "__main__":
    asyncio.run(main())
