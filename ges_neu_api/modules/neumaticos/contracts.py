"""
Contratos (interfaces) para el módulo de neumáticos.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .schemas import (
    NeumaticoCreate, NeumaticoUpdate, NeumaticoResponse,
    FabricanteCreate, FabricanteUpdate, FabricanteResponse,
    ModeloCreate, ModeloUpdate, ModeloResponse
)


class NeumaticoServiceContract(ABC):
    """Contrato para el servicio de neumáticos."""
    
    # Métodos para Neumáticos
    @abstractmethod
    async def create_neumatico(self, neumatico_data: NeumaticoCreate) -> NeumaticoResponse:
        """Crear un nuevo neumático."""
        pass
    
    @abstractmethod
    async def get_neumatico(self, neumatico_id: UUID) -> Optional[NeumaticoResponse]:
        """Obtener un neumático por ID."""
        pass
    
    @abstractmethod
    async def get_neumaticos(self, skip: int = 0, limit: int = 100) -> List[NeumaticoResponse]:
        """Obtener lista de neumáticos."""
        pass
    
    @abstractmethod
    async def update_neumatico(self, neumatico_id: UUID, neumatico_data: NeumaticoUpdate) -> Optional[NeumaticoResponse]:
        """Actualizar un neumático."""
        pass
    
    @abstractmethod
    async def delete_neumatico(self, neumatico_id: UUID) -> bool:
        """Eliminar un neumático."""
        pass
    
    # Métodos para Fabricantes
    @abstractmethod
    async def create_fabricante(self, fabricante_data: FabricanteCreate) -> FabricanteResponse:
        """Crear un nuevo fabricante."""
        pass
    
    @abstractmethod
    async def get_fabricante(self, fabricante_id: UUID) -> Optional[FabricanteResponse]:
        """Obtener un fabricante por ID."""
        pass
    
    @abstractmethod
    async def get_fabricantes(self, skip: int = 0, limit: int = 100) -> List[FabricanteResponse]:
        """Obtener lista de fabricantes."""
        pass
    
    @abstractmethod
    async def update_fabricante(self, fabricante_id: UUID, fabricante_data: FabricanteUpdate) -> Optional[FabricanteResponse]:
        """Actualizar un fabricante."""
        pass
    
    @abstractmethod
    async def delete_fabricante(self, fabricante_id: UUID) -> bool:
        """Eliminar un fabricante."""
        pass
    
    # Métodos para Modelos
    @abstractmethod
    async def create_modelo(self, modelo_data: ModeloCreate) -> ModeloResponse:
        """Crear un nuevo modelo."""
        pass
    
    @abstractmethod
    async def get_modelo(self, modelo_id: UUID) -> Optional[ModeloResponse]:
        """Obtener un modelo por ID."""
        pass
    
    @abstractmethod
    async def get_modelos(self, skip: int = 0, limit: int = 100) -> List[ModeloResponse]:
        """Obtener lista de modelos."""
        pass
    
    @abstractmethod
    async def update_modelo(self, modelo_id: UUID, modelo_data: ModeloUpdate) -> Optional[ModeloResponse]:
        """Actualizar un modelo."""
        pass
    
    @abstractmethod
    async def delete_modelo(self, modelo_id: UUID) -> bool:
        """Eliminar un modelo."""
        pass