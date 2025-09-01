"""
Script para verificar todos los imports de modelos funcionando correctamente
"""
import sys
import traceback

def test_import(module_path, class_name):
    """Test import of a specific class from a module"""
    try:
        module = __import__(module_path, fromlist=[class_name])
        getattr(module, class_name)
        print(f"OK {module_path}.{class_name}")
        return True
    except Exception as e:
        print(f"ERROR {module_path}.{class_name} - {str(e)}")
        return False

def main():
    print("=== TESTING MODEL IMPORTS ===\n")
    
    # Test auth models
    print("AUTH MODELS:")
    auth_success = all([
        test_import("ges_neu_api.modules.auth.models", "Usuario"),
        test_import("ges_neu_api.modules.auth.models", "Rol"),
        test_import("ges_neu_api.modules.auth.models", "Permiso"),
    ])
    
    print("\nVEHICULOS MODELS:")
    vehiculos_success = all([
        test_import("ges_neu_api.modules.vehiculos.models", "Vehiculos"),
        test_import("ges_neu_api.modules.vehiculos.models", "TiposVehiculo"),
        test_import("ges_neu_api.modules.vehiculos.models", "ConfiguracionesEje"),
    ])
    
    print("\nNEUMATICOS MODELS:")
    # Test neumaticos models from different files
    neumaticos_files = [
        "ges_neu_api.modules.neumaticos.models_final",
        "ges_neu_api.modules.neumaticos.models"
    ]
    
    neumaticos_success = False
    for module_path in neumaticos_files:
        try:
            print(f"  Testing {module_path}...")
            test_import(module_path, "FabricanteNeumatico")
            test_import(module_path, "ModeloNeumatico") 
            neumaticos_success = True
            break
        except:
            continue
    
    print(f"\nSUMMARY:")
    print(f"Auth models: {'OK' if auth_success else 'ERROR'}")
    print(f"Vehiculos models: {'OK' if vehiculos_success else 'ERROR'}")
    print(f"Neumaticos models: {'OK' if neumaticos_success else 'ERROR'}")
    
    # List all available model files
    print(f"\nAVAILABLE MODEL FILES:")
    import os
    modules_dir = "ges_neu_api/modules"
    for root, dirs, files in os.walk(modules_dir):
        for file in files:
            if file.endswith("models.py") or file.endswith("models_final.py"):
                rel_path = os.path.relpath(os.path.join(root, file))
                print(f"  - {rel_path}")

if __name__ == "__main__":
    main()
