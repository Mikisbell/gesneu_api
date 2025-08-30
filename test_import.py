# test_import.py

import sys
from os.path import abspath, dirname

# Añadimos la raíz del proyecto al path de Python, igual que en env.py
# para que pueda encontrar la carpeta 'ges_neu_api'
project_root = dirname(abspath(__file__))
sys.path.insert(0, project_root)

print("--- Iniciando prueba de diagnóstico de importaciones ---")
print(f"Ruta del proyecto añadida al path: {project_root}")

print("\n--- 1. Intentando importar 'Usuario' ---")
try:
    from ges_neu_api.modules.auth.models.usuario import Usuario
    print("✅ ¡ÉXITO! Se pudo importar la clase 'Usuario'.")
except ImportError as e:
    print(f"❌ ¡FALLÓ! No se pudo importar la clase 'Usuario'.")
    print(f"   Error exacto: {e}")
except Exception as e:
    print(f"❌ ¡FALLÓ con un error inesperado!")
    print(f"   Error exacto: {e}")

print("\n--- 2. Intentando importar 'Fabricante' y 'ModeloNeumatico' ---")
try:
    from ges_neu_api.modules.neumaticos.models import Fabricante, ModeloNeumatico
    print("✅ ¡ÉXITO! Se pudieron importar las clases de 'catalogos'.")
except ImportError as e:
    print(f"❌ ¡FALLÓ! No se pudieron importar las clases de 'catalogos'.")
    print(f"   Error exacto: {e}")
except Exception as e:
    print(f"❌ ¡FALLÓ con un error inesperado!")
    print(f"   Error exacto: {e}")

print("\n--- Prueba de diagnóstico finalizada ---")