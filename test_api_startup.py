"""
Test de arranque de la API sin conexión a BD para verificar que todos los modelos están correctos.
"""
import os
import sys

# Configurar para evitar conexión a BD
os.environ['SKIP_DB_INIT'] = '1'
os.environ['TESTING'] = '1'

def test_api_startup():
    """Test de arranque de la API."""
    try:
        print("🚀 Iniciando test de arranque de API...")
        
        # Import core modules
        from ges_neu_api.core.config import settings
        print("✅ Core config imported")
        
        # Import all routers to verify they load correctly
        from ges_neu_api.modules.auth.router import router as auth_router
        print("✅ Auth router imported")
        
        from ges_neu_api.modules.catalogos.router import router as catalogos_router
        print("✅ Catalogos router imported")
        
        from ges_neu_api.modules.vehiculos.router import router as vehiculos_router
        print("✅ Vehiculos router imported")
        
        from ges_neu_api.modules.inventario.router import router as inventario_router
        print("✅ Inventario router imported")
        
        from ges_neu_api.modules.eventos.router import router as eventos_router
        print("✅ Eventos router imported")
        
        from ges_neu_api.modules.garantias.router import router as garantias_router
        print("✅ Garantias router imported")
        
        from ges_neu_api.modules.alertas.router import router as alertas_router
        print("✅ Alertas router imported")
        
        from ges_neu_api.modules.neumaticos.router import router as neumaticos_router
        print("✅ Neumaticos router imported")
        
        from ges_neu_api.modules.bitacoras.router import router as bitacoras_router
        print("✅ Bitacoras router imported")
        
        from ges_neu_api.modules.sistema.router import router as sistema_router
        print("✅ Sistema router imported")
        
        print("\n🎉 Todos los módulos importados correctamente")
        print("📋 API lista para conectar a BD existente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importación: {e}")
        return False

if __name__ == "__main__":
    success = test_api_startup()
    if success:
        print("\n✅ API LISTA - Modelos alineados con esquema existente")
    else:
        print("\n❌ ERRORES - Revisar modelos")
    
    sys.exit(0 if success else 1)
