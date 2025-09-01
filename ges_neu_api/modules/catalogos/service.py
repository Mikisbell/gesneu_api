"""
Servicios para el módulo de catálogos.
Maneja la lógica de negocio para Proveedor, MotivoDesecho, Almacen y ParametroInventario.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import models, schemas


class CatalogService:
    """Servicio para operaciones CRUD de catálogos."""

    # --- CRUD para Proveedor ---
    
    async def create_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_data: schemas.ProveedorCreate
    ) -> schemas.ProveedorRead:
        """Crear un nuevo proveedor."""
        db_proveedor = models.Proveedor(**proveedor_data.model_dump())
        db.add(db_proveedor)
        await db.commit()
        await db.refresh(db_proveedor)
        return schemas.ProveedorRead.model_validate(db_proveedor)

    async def get_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_id: UUID
    ) -> Optional[schemas.ProveedorRead]:
        """Obtener un proveedor por ID."""
        result = await db.execute(
            select(models.Proveedor).where(
                models.Proveedor.id == proveedor_id,
                models.Proveedor.activo == True
            )
        )
        proveedor = result.scalar_one_or_none()
        return schemas.ProveedorRead.model_validate(proveedor) if proveedor else None

    async def get_proveedores(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.ProveedorRead]:
        """Obtener lista de proveedores."""
        result = await db.execute(
            select(models.Proveedor)
            .where(models.Proveedor.activo == True)
            .offset(skip)
            .limit(limit)
        )
        proveedores = result.scalars().all()
        return [schemas.ProveedorRead.model_validate(p) for p in proveedores]

    async def update_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_id: UUID, 
        proveedor_data: schemas.ProveedorUpdate
    ) -> Optional[schemas.ProveedorRead]:
        """Actualizar un proveedor."""
        result = await db.execute(
            select(models.Proveedor).where(models.Proveedor.id == proveedor_id)
        )
        proveedor = result.scalar_one_or_none()
        if not proveedor:
            return None
        
        update_data = proveedor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proveedor, field, value)
        
        await db.commit()
        await db.refresh(proveedor)
        return schemas.ProveedorRead.model_validate(proveedor)

    async def delete_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_id: UUID
    ) -> bool:
        """Eliminar un proveedor."""
        result = await db.execute(
            select(models.Proveedor).where(models.Proveedor.id == proveedor_id)
        )
        proveedor = result.scalar_one_or_none()
        if not proveedor:
            return False
        
        proveedor.activo = False
        await db.commit()
        return True

    # --- CRUD para MotivoDesecho ---
    
    async def create_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_data: schemas.MotivoDesechoCreate
    ) -> schemas.MotivoDesechoRead:
        """Crear un nuevo motivo de desecho."""
        db_motivo = models.MotivoDesecho(**motivo_data.model_dump())
        db.add(db_motivo)
        await db.commit()
        await db.refresh(db_motivo)
        return schemas.MotivoDesechoRead.model_validate(db_motivo)

    async def get_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_id: UUID
    ) -> Optional[schemas.MotivoDesechoRead]:
        """Obtener un motivo de desecho por ID."""
        result = await db.execute(
            select(models.MotivoDesecho).where(
                models.MotivoDesecho.id == motivo_id,
                models.MotivoDesecho.activo == True
            )
        )
        motivo = result.scalar_one_or_none()
        return schemas.MotivoDesechoRead.model_validate(motivo) if motivo else None

    async def get_motivos_desecho(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.MotivoDesechoRead]:
        """Obtener lista de motivos de desecho."""
        result = await db.execute(
            select(models.MotivoDesecho)
            .where(models.MotivoDesecho.activo == True)
            .offset(skip)
            .limit(limit)
        )
        motivos = result.scalars().all()
        return [schemas.MotivoDesechoRead.model_validate(m) for m in motivos]

    async def update_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_id: UUID, 
        motivo_data: schemas.MotivoDesechoUpdate
    ) -> Optional[schemas.MotivoDesechoRead]:
        """Actualizar un motivo de desecho."""
        result = await db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
        )
        motivo = result.scalar_one_or_none()
        if not motivo:
            return None
        
        update_data = motivo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(motivo, field, value)
        
        await db.commit()
        await db.refresh(motivo)
        return schemas.MotivoDesechoRead.model_validate(motivo)

    async def delete_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_id: UUID
    ) -> bool:
        """Eliminar un motivo de desecho."""
        result = await db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
        )
        motivo = result.scalar_one_or_none()
        if not motivo:
            return False
        
        motivo.activo = False
        await db.commit()
        return True

    # --- CRUD para Almacen ---
    
    async def create_almacen(
        self, 
        db: AsyncSession, 
        almacen_data: schemas.AlmacenCreate
    ) -> schemas.AlmacenRead:
        """Crear un nuevo almacén."""
        db_almacen = models.Almacen(**almacen_data.model_dump())
        db.add(db_almacen)
        await db.commit()
        await db.refresh(db_almacen)
        return schemas.AlmacenRead.model_validate(db_almacen)

    async def get_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID
    ) -> Optional[schemas.AlmacenRead]:
        """Obtener un almacén por ID."""
        result = await db.execute(
            select(models.Almacen).where(
                models.Almacen.id == almacen_id,
                models.Almacen.activo == True
            )
        )
        almacen = result.scalar_one_or_none()
        return schemas.AlmacenRead.model_validate(almacen) if almacen else None

    async def get_almacenes(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.AlmacenRead]:
        """Obtener lista de almacenes."""
        result = await db.execute(
            select(models.Almacen)
            .where(models.Almacen.activo == True)
            .offset(skip)
            .limit(limit)
        )
        almacenes = result.scalars().all()
        return [schemas.AlmacenRead.model_validate(a) for a in almacenes]

    async def update_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID, 
        almacen_data: schemas.AlmacenUpdate
    ) -> Optional[schemas.AlmacenRead]:
        """Actualizar un almacén."""
        result = await db.execute(
            select(models.Almacen).where(models.Almacen.id == almacen_id)
        )
        almacen = result.scalar_one_or_none()
        if not almacen:
            return None
        
        update_data = almacen_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(almacen, field, value)
        
        await db.commit()
        await db.refresh(almacen)
        return schemas.AlmacenRead.model_validate(almacen)

    async def delete_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID
    ) -> bool:
        """Eliminar un almacén."""
        result = await db.execute(
            select(models.Almacen).where(models.Almacen.id == almacen_id)
        )
        almacen = result.scalar_one_or_none()
        if not almacen:
            return False
        
        almacen.activo = False
        await db.commit()
        return True

    # --- CRUD para ParametroInventario ---
    
    async def create_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_data: schemas.ParametroInventarioCreate
    ) -> schemas.ParametroInventarioRead:
        """Crear un nuevo parámetro de inventario."""
        db_parametro = models.ParametroInventario(**parametro_data.model_dump())
        db.add(db_parametro)
        await db.commit()
        await db.refresh(db_parametro)
        return schemas.ParametroInventarioRead.model_validate(db_parametro)

    async def get_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID
    ) -> Optional[schemas.ParametroInventarioRead]:
        """Obtener un parámetro de inventario por ID."""
        result = await db.execute(
            select(models.ParametroInventario).where(
                models.ParametroInventario.id == parametro_id,
                models.ParametroInventario.activo == True
            )
        )
        parametro = result.scalar_one_or_none()
        return schemas.ParametroInventarioRead.model_validate(parametro) if parametro else None

    async def get_parametros_inventario(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.ParametroInventarioRead]:
        """Obtener lista de parámetros de inventario."""
        result = await db.execute(
            select(models.ParametroInventario)
            .where(models.ParametroInventario.activo == True)
            .offset(skip)
            .limit(limit)
        )
        parametros = result.scalars().all()
        return [schemas.ParametroInventarioRead.model_validate(p) for p in parametros]

    async def update_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID, 
        parametro_data: schemas.ParametroInventarioUpdate
    ) -> Optional[schemas.ParametroInventarioRead]:
        """Actualizar un parámetro de inventario."""
        result = await db.execute(
            select(models.ParametroInventario).where(models.ParametroInventario.id == parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            return None
        
        update_data = parametro_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(parametro, field, value)
        
        await db.commit()
        await db.refresh(parametro)
        return schemas.ParametroInventarioRead.model_validate(parametro)

    async def delete_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID
    ) -> bool:
        """Eliminar un parámetro de inventario."""
        result = await db.execute(
            select(models.ParametroInventario).where(models.ParametroInventario.id == parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            return False
        
        parametro.activo = False
        await db.commit()
        return True


# Create service instance
catalog_service = CatalogService()
