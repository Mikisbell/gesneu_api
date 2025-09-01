from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas


class CatalogServiceContract(ABC):
    """Contrato para servicios de catálogos."""

    @abstractmethod
    async def create_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_data: schemas.ProveedorCreate
    ) -> schemas.ProveedorRead:
        """Crear un nuevo proveedor."""
        pass

    @abstractmethod
    async def get_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_id: UUID
    ) -> Optional[schemas.ProveedorRead]:
        """Obtener un proveedor por ID."""
        pass

    @abstractmethod
    async def get_proveedores(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.ProveedorRead]:
        """Obtener lista de proveedores."""
        pass

    @abstractmethod
    async def update_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_id: UUID, 
        proveedor_data: schemas.ProveedorUpdate
    ) -> Optional[schemas.ProveedorRead]:
        """Actualizar un proveedor."""
        pass

    @abstractmethod
    async def delete_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_id: UUID
    ) -> bool:
        """Eliminar un proveedor."""
        pass

    @abstractmethod
    async def create_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_data: schemas.MotivoDesechoCreate
    ) -> schemas.MotivoDesechoRead:
        """Crear un nuevo motivo de desecho."""
        pass

    @abstractmethod
    async def get_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_id: UUID
    ) -> Optional[schemas.MotivoDesechoRead]:
        """Obtener un motivo de desecho por ID."""
        pass

    @abstractmethod
    async def get_motivos_desecho(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.MotivoDesechoRead]:
        """Obtener lista de motivos de desecho."""
        pass

    @abstractmethod
    async def update_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_id: UUID, 
        motivo_data: schemas.MotivoDesechoUpdate
    ) -> Optional[schemas.MotivoDesechoRead]:
        """Actualizar un motivo de desecho."""
        pass

    @abstractmethod
    async def delete_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_id: UUID
    ) -> bool:
        """Eliminar un motivo de desecho."""
        pass

    @abstractmethod
    async def create_almacen(
        self, 
        db: AsyncSession, 
        almacen_data: schemas.AlmacenCreate
    ) -> schemas.AlmacenRead:
        """Crear un nuevo almacén."""
        pass

    @abstractmethod
    async def get_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID
    ) -> Optional[schemas.AlmacenRead]:
        """Obtener un almacén por ID."""
        pass

    @abstractmethod
    async def get_almacenes(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.AlmacenRead]:
        """Obtener lista de almacenes."""
        pass

    @abstractmethod
    async def update_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID, 
        almacen_data: schemas.AlmacenUpdate
    ) -> Optional[schemas.AlmacenRead]:
        """Actualizar un almacén."""
        pass

    @abstractmethod
    async def delete_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID
    ) -> bool:
        """Eliminar un almacén."""
        pass

    @abstractmethod
    async def create_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_data: schemas.ParametroInventarioCreate
    ) -> schemas.ParametroInventarioRead:
        """Crear un nuevo parámetro de inventario."""
        pass

    @abstractmethod
    async def get_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID
    ) -> Optional[schemas.ParametroInventarioRead]:
        """Obtener un parámetro de inventario por ID."""
        pass

    @abstractmethod
    async def get_parametros_inventario(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.ParametroInventarioRead]:
        """Obtener lista de parámetros de inventario."""
        pass

    @abstractmethod
    async def update_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID, 
        parametro_data: schemas.ParametroInventarioUpdate
    ) -> Optional[schemas.ParametroInventarioRead]:
        """Actualizar un parámetro de inventario."""
        pass

    @abstractmethod
    async def delete_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID
    ) -> bool:
        """Eliminar un parámetro de inventario."""
        pass