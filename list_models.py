"""
Lista todos los modelos SQLModel definidos en el proyecto.
"""
import sys
from pathlib import Path

# Añadir el directorio raíz al path
project_root = str(Path(__file__).parent.resolve())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Diccionario para almacenar los modelos por módulo
models_by_module = {}

# Función para registrar modelos
def register_models(module_name, *models):
    if module_name not in models_by_module:
        models_by_module[module_name] = []
    for model in models:
        models_by_module[module_name].append(model.__name__)

# Importar y registrar modelos (sin ejecutar código de inicialización)
print("Cargando modelos...\n")

try:
    # Auth
    from ges_neu_api.modules.auth.models import Usuario, Rol, Permiso
    register_models("auth", Usuario, Rol, Permiso)
    
    # Vehículos
    from ges_neu_api.modules.vehiculos.models import Vehiculo, TipoVehiculo, ConfiguracionEje, PosicionNeumatico
    register_models("vehiculos", Vehiculo, TipoVehiculo, ConfiguracionEje, PosicionNeumatico)
    
    # Neumáticos
    from ges_neu_api.modules.neumaticos.models import Neumatico, ModeloNeumatico, FabricanteNeumatico
    register_models("neumaticos", Neumatico, ModeloNeumatico, FabricanteNeumatico)
    
    # Inventario
    from ges_neu_api.modules.inventario.models import InventarioNeumaticos, MovimientoInventario
    register_models("inventario", InventarioNeumaticos, MovimientoInventario)
    
    # Eventos
    from ges_neu_api.modules.eventos.models import EventoNeumatico, HistorialEstadoNeumatico, MedicionProfundidad
    register_models("eventos", EventoNeumatico, HistorialEstadoNeumatico, MedicionProfundidad)
    
    # Garantías
    from ges_neu_api.modules.garantias.models import GarantiaNeumatico
    register_models("garantias", GarantiaNeumatico)
    
    # Alertas
    from ges_neu_api.modules.alertas.models import Alerta
    register_models("alertas", Alerta)
    
    # Catálogos
    from ges_neu_api.modules.catalogos.models import Proveedor, Almacen, MotivoDesecho
    register_models("catalogos", Proveedor, Almacen, MotivoDesecho)
    
    # Bitácoras
    from ges_neu_api.modules.bitacoras.models import BitacoraOperacion
    register_models("bitacoras", BitacoraOperacion)
    
    # Mostrar resumen
    print("\n=== MODELOS ENCONTRADOS ===\n")
    for module, models in models_by_module.items():
        print(f"Módulo: {module.upper()}")
        for model in sorted(models):
            print(f"  - {model}")
        print()
    
    total_models = sum(len(models) for models in models_by_module.values())
    print(f"\nTotal de modelos: {total_models}")

except ImportError as e:
    print(f"\n[ERROR] Error al importar modelos: {e}")
    print("Asegúrate de que todos los módulos estén correctamente instalados.")
except Exception as e:
    print(f"\n[ERROR] Error inesperado: {e}")
