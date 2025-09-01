from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from .models import Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico, RegistrosOdometro
from .schemas import (
    VehiculoCreate, VehiculoUpdate,
    TiposVehiculoCreate, TiposVehiculoUpdate,
    ConfiguracionesEjeCreate, ConfiguracionesEjeUpdate,
    PosicionesNeumaticoCreate, PosicionesNeumaticoUpdate,
    RegistrosOdometroCreate, RegistrosOdometroUpdate
)


class VehiculosServiceContract(ABC):
    """Contrato para el servicio de vehículos."""
    
    # Vehiculos CRUD
    @abstractmethod
    async def get_vehiculo(self, vehiculo_id: UUID) -> Optional[Vehiculos]:
        """Obtiene un vehículo por su ID."""
        pass
    
    @abstractmethod
    async def get_multi_vehiculos(self, skip: int = 0, limit: int = 100) -> List[Vehiculos]:
        """Obtiene múltiples vehículos con paginación."""
        pass
    
    @abstractmethod
    async def create_vehiculo(self, obj_in: VehiculoCreate) -> Vehiculos:
        """Crea un nuevo vehículo."""
        pass
    
    @abstractmethod
    async def update_vehiculo(self, vehiculo_id: UUID, obj_in: VehiculoUpdate) -> Optional[Vehiculos]:
        """Actualiza un vehículo existente."""
        pass
    
    @abstractmethod
    async def delete_vehiculo(self, vehiculo_id: UUID) -> Optional[UUID]:
        """Elimina un vehículo."""
        pass
    
    # TiposVehiculo CRUD
    @abstractmethod
    async def get_tipo_vehiculo(self, tipo_id: UUID) -> Optional[TiposVehiculo]:
        """Obtiene un tipo de vehículo por su ID."""
        pass
    
    @abstractmethod
    async def get_multi_tipos_vehiculo(self, skip: int = 0, limit: int = 100) -> List[TiposVehiculo]:
        """Obtiene múltiples tipos de vehículo."""
        pass
    
    @abstractmethod
    async def create_tipo_vehiculo(self, obj_in: TiposVehiculoCreate) -> TiposVehiculo:
        """Crea un nuevo tipo de vehículo."""
        pass