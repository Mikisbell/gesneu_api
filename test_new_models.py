"""
Script para verificar que los nuevos modelos se pueden importar correctamente
sin depender de la conexión a la base de datos.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_inventario_models():
    """Test importación de modelos de inventario."""
    try:
        from ges_neu_api.modules.inventario.models import InventarioNeumaticos, MovimientosInventario, TipoMovimientoEnum
        print("✅ Modelos de inventario importados correctamente")
        print(f"   - InventarioNeumaticos: {InventarioNeumaticos.__tablename__}")
        print(f"   - MovimientosInventario: {MovimientosInventario.__tablename__}")
        return True
    except Exception as e:
        print(f"❌ Error importando modelos de inventario: {e}")
        return False

def test_eventos_models():
    """Test importación de modelos de eventos."""
    try:
        from ges_neu_api.modules.eventos.models import EventosNeumaticos, HistorialEstadosNeumaticos, MedicionesProfundidad
        print("✅ Modelos de eventos importados correctamente")
        print(f"   - EventosNeumaticos: {EventosNeumaticos.__tablename__}")
        print(f"   - HistorialEstadosNeumaticos: {HistorialEstadosNeumaticos.__tablename__}")
        print(f"   - MedicionesProfundidad: {MedicionesProfundidad.__tablename__}")
        return True
    except Exception as e:
        print(f"❌ Error importando modelos de eventos: {e}")
        return False

def test_garantias_models():
    """Test importación de modelos de garantías."""
    try:
        from ges_neu_api.modules.garantias.models import GarantiasNeumaticos
        print("✅ Modelos de garantías importados correctamente")
        print(f"   - GarantiasNeumaticos: {GarantiasNeumaticos.__tablename__}")
        return True
    except Exception as e:
        print(f"❌ Error importando modelos de garantías: {e}")
        return False

def test_alertas_models():
    """Test importación de modelos de alertas."""
    try:
        from ges_neu_api.modules.alertas.models import Alertas, TipoAlertaEnum, PrioridadAlertaEnum, EstadoAlertaEnum
        print("✅ Modelos de alertas importados correctamente")
        print(f"   - Alertas: {Alertas.__tablename__}")
        return True
    except Exception as e:
        print(f"❌ Error importando modelos de alertas: {e}")
        return False

def test_existing_models():
    """Test importación de modelos existentes."""
    try:
        from ges_neu_api.modules.auth.models import Usuario, Rol, Permiso
        from ges_neu_api.modules.vehiculos.models import Vehiculos, TiposVehiculo
        from ges_neu_api.modules.catalogos.models import Proveedor, Almacen
        from ges_neu_api.modules.neumaticos.models import Neumatico, ModeloNeumatico
        print("✅ Modelos existentes importados correctamente")
        return True
    except Exception as e:
        print(f"❌ Error importando modelos existentes: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando importación de modelos...")
    print("=" * 50)
    
    results = []
    results.append(test_existing_models())
    results.append(test_inventario_models())
    results.append(test_eventos_models())
    results.append(test_garantias_models())
    results.append(test_alertas_models())
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ÉXITO: Todos los modelos ({passed}/{total}) se importan correctamente")
    else:
        print(f"⚠️  PARCIAL: {passed}/{total} grupos de modelos importados correctamente")
