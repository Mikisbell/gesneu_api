#!/usr/bin/env python3
"""
Test de importación aislada para identificar conflictos de metadatos SQLAlchemy.
"""
import os
import sys

# Configurar entorno para evitar conexión a BD
os.environ['SKIP_DB_INIT'] = '1'

def test_individual_module_imports():
    """Prueba la importación de cada módulo individualmente."""
    
    modules_to_test = [
        'ges_neu_api.core.base_models',
        'ges_neu_api.modules.auth.models',
        'ges_neu_api.modules.vehiculos.models',
        'ges_neu_api.modules.catalogos.models',
        'ges_neu_api.modules.neumaticos.models',
        'ges_neu_api.modules.inventario.models',
        'ges_neu_api.modules.eventos.models',
        'ges_neu_api.modules.garantias.models',
        'ges_neu_api.modules.alertas.models',
        'ges_neu_api.modules.bitacoras.models',
    ]
    
    for module_name in modules_to_test:
        try:
            print(f"Importando {module_name}...")
            __import__(module_name)
            print(f"✅ {module_name} - OK")
        except Exception as e:
            print(f"❌ {module_name} - ERROR: {e}")
            return False
    
    return True

def test_combined_imports():
    """Prueba la importación combinada de todos los módulos."""
    try:
        print("\n=== PRUEBA DE IMPORTACIÓN COMBINADA ===")
        
        # Importar todos los modelos en orden
        from ges_neu_api.core.base_models import BaseModel
        print("✅ BaseModel importado")
        
        from ges_neu_api.modules.auth.models import Usuario, Rol, Permiso
        print("✅ Modelos auth importados")
        
        from ges_neu_api.modules.vehiculos.models import Vehiculos, TiposVehiculo
        print("✅ Modelos vehiculos importados")
        
        from ges_neu_api.modules.catalogos.models import Almacen, Proveedor
        print("✅ Modelos catalogos importados")
        
        from ges_neu_api.modules.neumaticos.models import FabricanteNeumatico, ModeloNeumatico, Neumatico
        print("✅ Modelos neumaticos importados")
        
        from ges_neu_api.modules.inventario.models import InventarioNeumaticos, MovimientosInventario
        print("✅ Modelos inventario importados")
        
        from ges_neu_api.modules.eventos.models import EventosNeumaticos
        print("✅ Modelos eventos importados")
        
        from ges_neu_api.modules.garantias.models import GarantiasNeumaticos
        print("✅ Modelos garantias importados")
        
        from ges_neu_api.modules.alertas.models import Alertas
        print("✅ Modelos alertas importados")
        
        from ges_neu_api.modules.bitacoras.models import BitacoraMantenimiento
        print("✅ Modelos bitacoras importados")
        
        print("\n✅ TODOS LOS MODELOS IMPORTADOS EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN IMPORTACIÓN COMBINADA: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== PRUEBA DE IMPORTACIÓN AISLADA ===")
    
    # Limpiar cualquier metadata previa
    from sqlalchemy import MetaData
    metadata = MetaData()
    
    success = test_individual_module_imports()
    
    if success:
        success = test_combined_imports()
    
    if success:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - MODELOS LISTOS")
    else:
        print("\n💥 FALLÓ - REVISAR CONFLICTOS DE METADATOS")
