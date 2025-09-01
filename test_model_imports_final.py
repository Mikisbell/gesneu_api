"""
Test final de importacion de todos los modelos sin conexion a BD
"""
import os
import sys

# Configurar path sin importar database
os.environ['SKIP_DB_INIT'] = '1'
sys.path.insert(0, '.')

def test_model_imports():
    """Test individual de cada modulo."""
    modules_to_test = [
        ('auth', ['Usuario', 'Rol', 'Permiso']),
        ('vehiculos', ['Vehiculos', 'TiposVehiculo']),
        ('catalogos', ['Proveedor', 'Almacen']),
        ('neumaticos', ['Neumatico', 'ModeloNeumatico']),
        ('inventario', ['InventarioNeumaticos', 'MovimientosInventario']),
        ('eventos', ['EventosNeumaticos', 'HistorialEstadosNeumaticos']),
        ('garantias', ['GarantiasNeumaticos']),
        ('alertas', ['Alertas'])
    ]
    
    results = []
    
    for module_name, models in modules_to_test:
        try:
            module_path = f'ges_neu_api.modules.{module_name}.models'
            module = __import__(module_path, fromlist=models)
            
            found_models = []
            for model in models:
                if hasattr(module, model):
                    found_models.append(model)
            
            print(f"✅ {module_name}: {len(found_models)}/{len(models)} modelos")
            results.append(len(found_models) == len(models))
            
        except Exception as e:
            print(f"❌ {module_name}: Error - {e}")
            results.append(False)
    
    return results

if __name__ == "__main__":
    print("🔍 Test de importacion de modelos...")
    print("=" * 50)
    
    results = test_model_imports()
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    if passed == total:
        print(f"🎉 EXITO: {passed}/{total} modulos importados")
    else:
        print(f"⚠️  PARCIAL: {passed}/{total} modulos importados")
