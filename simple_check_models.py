"""
Script simple para verificar la definición de los modelos sin base de datos.
"""
import sys
from pathlib import Path
from typing import List, Type
from sqlmodel import SQLModel

# Asegurarse de que el directorio raíz del proyecto está en el path
project_root = str(Path(__file__).parent.resolve())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar todos los modelos
from ges_neu_api.modules.auth.models import Usuario, Rol, Permiso
from ges_neu_api.modules.vehiculos.models import Vehiculo, TipoVehiculo, ConfiguracionEje, PosicionNeumatico
from ges_neu_api.modules.neumaticos.models import Neumatico, ModeloNeumatico, FabricanteNeumatico
from ges_neu_api.modules.inventario.models import InventarioNeumaticos, MovimientoInventario
from ges_neu_api.modules.eventos.models import EventoNeumatico, HistorialEstadoNeumatico, MedicionProfundidad
from ges_neu_api.modules.garantias.models import GarantiaNeumatico
from ges_neu_api.modules.alertas.models import Alerta
from ges_neu_api.modules.catalogos.models import Proveedor, Almacen, MotivoDesecho
from ges_neu_api.modules.bitacoras.models import BitacoraOperacion

def get_model_info(model: Type[SQLModel]) -> str:
    """Obtiene información detallada de un modelo."""
    table_name = model.__tablename__ if hasattr(model, '__tablename__') else 'NO DEFINIDA'
    fields = []
    
    # Obtener campos del modelo
    for name, field in model.model_fields.items():
        field_type = field.annotation.__name__ if hasattr(field.annotation, '__name__') else str(field.annotation)
        field_info = f"  - {name}: {field_type}"
        
        # Agregar información adicional
        if field.is_required():
            field_info += " (Requerido)"
        if field.default is not None:
            field_info += f" (Default: {field.default})"
        if field.description:
            field_info += f" - {field.description}"
            
        fields.append(field_info)
    
    # Construir la salida
    output = [f"\n=== MODELO: {model.__name__} ==="]
    output.append(f"Tabla: {table_name}")
    output.append("\nCAMPOS:")
    output.extend(fields)
    
    return "\n".join(output)

def main():
    """Función principal."""
    # Lista de todos los modelos a verificar
    models: List[Type[SQLModel]] = [
        # Auth
        Usuario, Rol, Permiso,
        
        # Vehículos
        Vehiculo, TipoVehiculo, ConfiguracionEje, PosicionNeumatico,
        
        # Neumáticos
        Neumatico, ModeloNeumatico, FabricanteNeumatico,
        
        # Inventario
        InventarioNeumaticos, MovimientoInventario,
        
        # Eventos
        EventoNeumatico, HistorialEstadoNeumatico, MedicionProfundidad,
        
        # Garantías
        GarantiaNeumatico,
        
        # Alertas
        Alerta,
        
        # Catálogos
        Proveedor, Almacen, MotivoDesecho,
        
        # Bitácoras
        BitacoraOperacion
    ]
    
    print("\n" + "="*80)
    print("VERIFICACIÓN DE MODELOS DE LA APLICACIÓN")
    print("="*80)
    
    for model in models:
        try:
            print(get_model_info(model))
            print("\n" + "-"*80)
        except Exception as e:
            print(f"\n[ERROR] Error procesando modelo {model.__name__}: {str(e)}\n")

if __name__ == "__main__":
    main()
