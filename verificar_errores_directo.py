#!/usr/bin/env python3
"""
Verificación directa de errores sin servidor - importando módulos directamente
"""
import asyncio
import sys
import traceback
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

async def test_inventory_import():
    """Probar importación del módulo de inventario"""
    print("🔍 Probando importación del módulo inventario...")
    try:
        from ges_neu_api.modules.inventario.models import ParametrosInventario, TipoParametroInventarioEnum
        from ges_neu_api.modules.inventario.schemas import ParametroInventarioResponse
        from ges_neu_api.modules.inventario.router import router as inventario_router
        print("✅ Importación de inventario exitosa")
        
        # Verificar que el router tenga rutas
        routes = [route.path for route in inventario_router.routes]
        print(f"   Rutas encontradas: {routes}")
        return True
    except Exception as e:
        print(f"❌ Error importando inventario: {str(e)}")
        print(traceback.format_exc())
        return False

async def test_neumaticos_import():
    """Probar importación del módulo neumáticos"""
    print("🔍 Probando importación del módulo neumáticos...")
    try:
        from ges_neu_api.modules.neumaticos.models import ModeloNeumatico
        from ges_neu_api.modules.neumaticos.schemas import ModeloResponse
        from ges_neu_api.modules.neumaticos.router import router as neumaticos_router
        print("✅ Importación de neumáticos exitosa")
        
        # Verificar que el router tenga rutas
        routes = [route.path for route in neumaticos_router.routes]
        print(f"   Rutas encontradas: {routes}")
        return True
    except Exception as e:
        print(f"❌ Error importando neumáticos: {str(e)}")
        print(traceback.format_exc())
        return False

async def test_enum_alignment():
    """Verificar alineación de enums"""
    print("🔍 Verificando alineación de enums...")
    try:
        from ges_neu_api.modules.inventario.models import TipoParametroInventarioEnum
        
        print("   Valores del enum TipoParametroInventarioEnum:")
        for item in TipoParametroInventarioEnum:
            print(f"     - {item.name}: {item.value}")
        
        # Verificar que coincidan con el esquema real
        expected_values = [
            'STOCK_MINIMO',
            'STOCK_MAXIMO', 
            'PROFUNDIDAD_MINIMA_RETIRO_MM',
            'PROFUNDIDAD_MINIMA_REENCAUCHE_MM',
            'TIEMPO_MAXIMO_VIDA_MESES',
            'MAX_ROTACIONES_PERIODO',
            'MAX_REPARACIONES_PERIODO',
            'VIDA_MAXIMA_ESTANTE_MESES_SIN_USO'
        ]
        
        actual_values = [item.value for item in TipoParametroInventarioEnum]
        missing = set(expected_values) - set(actual_values)
        extra = set(actual_values) - set(expected_values)
        
        if missing:
            print(f"   ❌ Valores faltantes: {missing}")
        if extra:
            print(f"   ❌ Valores extra: {extra}")
        if not missing and not extra:
            print("   ✅ Enum perfectamente alineado")
            
        return len(missing) == 0 and len(extra) == 0
    except Exception as e:
        print(f"❌ Error verificando enums: {str(e)}")
        print(traceback.format_exc())
        return False

async def test_main_app_import():
    """Probar importación de la app principal"""
    print("🔍 Probando importación de la app principal...")
    try:
        from ges_neu_api.main import app
        print("✅ Importación de app principal exitosa")
        
        # Verificar routers registrados
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"   Rutas principales: {routes[:10]}...")  # Mostrar solo las primeras 10
        return True
    except Exception as e:
        print(f"❌ Error importando app principal: {str(e)}")
        print(traceback.format_exc())
        return False

async def main():
    """Ejecutar todas las verificaciones"""
    print("VERIFICACIÓN DIRECTA DE ERRORES")
    print("=" * 50)
    
    tests = [
        ("Inventario", test_inventory_import),
        ("Neumáticos", test_neumaticos_import), 
        ("Enums", test_enum_alignment),
        ("App Principal", test_main_app_import)
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n{'-' * 30}")
        results[name] = await test_func()
    
    print(f"\n{'=' * 50}")
    print("RESUMEN DE RESULTADOS:")
    for name, success in results.items():
        status = "✅ OK" if success else "❌ FALLO"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nEstado general: {'✅ TODOS OK' if all_passed else '❌ HAY ERRORES'}")

if __name__ == "__main__":
    asyncio.run(main())
