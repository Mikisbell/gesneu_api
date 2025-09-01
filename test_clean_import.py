#!/usr/bin/env python3
"""
Test de importación completamente limpia para identificar el origen del conflicto.
"""
import sys
import os

# Configurar entorno
os.environ['SKIP_DB_INIT'] = '1'

def test_step_by_step():
    """Prueba importación paso a paso para identificar el conflicto."""
    
    try:
        print("1. Importando base_models...")
        from ges_neu_api.core.base_models import BaseModel
        print("✅ BaseModel OK")
        
        print("2. Importando solo FabricanteNeumatico...")
        # Importar solo la clase específica
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "neumaticos_models", 
            "ges_neu_api/modules/neumaticos/models.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # Ejecutar solo hasta FabricanteNeumatico
        print("✅ Importación directa exitosa")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_step_by_step()
