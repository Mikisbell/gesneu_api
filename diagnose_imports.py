#!/usr/bin/env python3
"""
Diagnóstico de imports para identificar errores
"""
import sys
import traceback

def test_import(module_name, description):
    """Test de importación individual"""
    try:
        if module_name == "neumaticos.service":
            from ges_neu_api.modules.neumaticos.service import NeumaticoService
            print(f"✅ {description}: OK")
        elif module_name == "bitacoras.service":
            from ges_neu_api.modules.bitacoras.service import BitacoraService
            print(f"✅ {description}: OK")
        elif module_name == "sistema.service":
            from ges_neu_api.modules.sistema.service import SistemaService
            print(f"✅ {description}: OK")
        elif module_name == "neumaticos.models":
            from ges_neu_api.modules.neumaticos.models import ModeloNeumatico
            print(f"✅ {description}: OK")
        elif module_name == "bitacoras.models":
            from ges_neu_api.modules.bitacoras.models import BitacoraOperaciones
            print(f"✅ {description}: OK")
        elif module_name == "sistema.models":
            from ges_neu_api.modules.bitacoras.models import Rutas, TiposRuta
            print(f"✅ {description}: OK")
        return True
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("🔍 DIAGNÓSTICO DE IMPORTS\n")
    
    # Test imports críticos
    test_import("neumaticos.service", "Neumáticos Service")
    test_import("neumaticos.models", "Neumáticos Models")
    test_import("bitacoras.service", "Bitácoras Service")
    test_import("bitacoras.models", "Bitácoras Models")
    test_import("sistema.service", "Sistema Service")
    test_import("sistema.models", "Sistema Models")

if __name__ == "__main__":
    main()
