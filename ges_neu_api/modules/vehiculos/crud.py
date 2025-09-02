from ges_neu_api.core.crud import CRUDBase
from .models import Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico, RegistrosOdometro
from .schemas import (
    VehiculoCreate, VehiculoUpdate, 
    TiposVehiculoCreate, TiposVehiculoUpdate, 
    ConfiguracionesEjeCreate, ConfiguracionesEjeUpdate, 
    PosicionesNeumaticoCreate, PosicionesNeumaticoUpdate, 
    RegistrosOdometroCreate, RegistrosOdometroUpdate
)

# Usar CRUD genérico que funciona en otros módulos
crud_vehiculo = CRUDBase[Vehiculos, VehiculoCreate, VehiculoUpdate](Vehiculos)
crud_tipos_vehiculo = CRUDBase[TiposVehiculo, TiposVehiculoCreate, TiposVehiculoUpdate](TiposVehiculo)
crud_configuraciones_eje = CRUDBase[ConfiguracionesEje, ConfiguracionesEjeCreate, ConfiguracionesEjeUpdate](ConfiguracionesEje)
crud_posiciones_neumatico = CRUDBase[PosicionesNeumatico, PosicionesNeumaticoCreate, PosicionesNeumaticoUpdate](PosicionesNeumatico)
crud_registros_odometro = CRUDBase[RegistrosOdometro, RegistrosOdometroCreate, RegistrosOdometroUpdate](RegistrosOdometro)
