"""
Servicios del módulo de neumáticos.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from .models import Neumatico, FabricanteNeumatico, ModeloNeumatico
from .schemas import (
    NeumaticoCreate, NeumaticoUpdate, NeumaticoResponse,
    FabricanteCreate, FabricanteUpdate, FabricanteResponse,
    ModeloCreate, ModeloUpdate, ModeloResponse
)
from .contracts import NeumaticoServiceContract


class NeumaticoService(NeumaticoServiceContract):
    """Servicio para gestión de neumáticos."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Servicios para Neumáticos
    async def create_neumatico(self, neumatico_data: NeumaticoCreate) -> NeumaticoResponse:
        """Crear un nuevo neumático."""
        neumatico = Neumatico(**neumatico_data.model_dump())
        self.db.add(neumatico)
        await self.db.commit()
        await self.db.refresh(neumatico)
        return NeumaticoResponse.model_validate(neumatico)
    
    async def get_neumatico(self, neumatico_id: UUID) -> Optional[NeumaticoResponse]:
        """Obtener un neumático por ID."""
        result = await self.db.execute(
            select(Neumatico).where(Neumatico.id == neumatico_id)
        )
        neumatico = result.scalar_one_or_none()
        if neumatico:
            return NeumaticoResponse.model_validate(neumatico)
        return None
    
    async def get_neumaticos(self, skip: int = 0, limit: int = 100) -> List[NeumaticoResponse]:
        """Obtener lista de neumáticos."""
        result = await self.db.execute(
            select(Neumatico).offset(skip).limit(limit)
        )
        neumaticos = result.scalars().all()
        return [NeumaticoResponse.model_validate(n) for n in neumaticos]
    
    async def update_neumatico(self, neumatico_id: UUID, neumatico_data: NeumaticoUpdate) -> Optional[NeumaticoResponse]:
        """Actualizar un neumático."""
        result = await self.db.execute(
            select(Neumatico).where(Neumatico.id == neumatico_id)
        )
        neumatico = result.scalar_one_or_none()
        if not neumatico:
            return None
        
        update_data = neumatico_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(neumatico, field, value)
        
        await self.db.commit()
        await self.db.refresh(neumatico)
        return NeumaticoResponse.model_validate(neumatico)
    
    async def delete_neumatico(self, neumatico_id: UUID) -> bool:
        """Eliminar un neumático."""
        result = await self.db.execute(
            select(Neumatico).where(Neumatico.id == neumatico_id)
        )
        neumatico = result.scalar_one_or_none()
        if not neumatico:
            return False
        
        await self.db.delete(neumatico)
        await self.db.commit()
        return True
    
    # Servicios para Fabricantes
    async def create_fabricante(self, fabricante_data: FabricanteCreate) -> FabricanteResponse:
        """Crear un nuevo fabricante."""
        fabricante = FabricanteNeumatico(**fabricante_data.model_dump())
        self.db.add(fabricante)
        await self.db.commit()
        await self.db.refresh(fabricante)
        return FabricanteResponse.model_validate(fabricante)
    
    async def get_fabricante(self, fabricante_id: UUID) -> Optional[FabricanteResponse]:
        """Obtener un fabricante por ID."""
        result = await self.db.execute(
            select(FabricanteNeumatico).where(FabricanteNeumatico.id == fabricante_id)
        )
        fabricante = result.scalar_one_or_none()
        if fabricante:
            return FabricanteResponse.model_validate(fabricante)
        return None
    
    async def get_fabricantes(self, skip: int = 0, limit: int = 100) -> List[FabricanteResponse]:
        """Obtener lista de fabricantes."""
        result = await self.db.execute(
            select(FabricanteNeumatico).offset(skip).limit(limit)
        )
        fabricantes = result.scalars().all()
        return [FabricanteResponse.model_validate(f) for f in fabricantes]
    
    async def update_fabricante(self, fabricante_id: UUID, fabricante_data: FabricanteUpdate) -> Optional[FabricanteResponse]:
        """Actualizar un fabricante."""
        result = await self.db.execute(
            select(FabricanteNeumatico).where(FabricanteNeumatico.id == fabricante_id)
        )
        fabricante = result.scalar_one_or_none()
        if not fabricante:
            return None
        
        update_data = fabricante_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fabricante, field, value)
        
        await self.db.commit()
        await self.db.refresh(fabricante)
        return FabricanteResponse.model_validate(fabricante)
    
    async def delete_fabricante(self, fabricante_id: UUID) -> bool:
        """Eliminar un fabricante."""
        result = await self.db.execute(
            select(FabricanteNeumatico).where(FabricanteNeumatico.id == fabricante_id)
        )
        fabricante = result.scalar_one_or_none()
        if not fabricante:
            return False
        
        await self.db.delete(fabricante)
        await self.db.commit()
        return True
    
    # Servicios para Modelos
    async def create_modelo(self, modelo_data: ModeloCreate) -> ModeloResponse:
        """Crear un nuevo modelo."""
        modelo = ModeloNeumatico(**modelo_data.model_dump())
        self.db.add(modelo)
        await self.db.commit()
        await self.db.refresh(modelo)
        return ModeloResponse.model_validate(modelo)
    
    async def get_modelo(self, modelo_id: UUID) -> Optional[ModeloResponse]:
        """Obtener un modelo por ID."""
        result = await self.db.execute(
            select(ModeloNeumatico).where(ModeloNeumatico.id == modelo_id)
        )
        modelo = result.scalar_one_or_none()
        if modelo:
            return ModeloResponse.model_validate(modelo)
        return None
    
    async def get_modelos(self, skip: int = 0, limit: int = 100) -> List[ModeloResponse]:
        """Obtener lista de modelos."""
        result = await self.db.execute(
            select(ModeloNeumatico).offset(skip).limit(limit)
        )
        modelos = result.scalars().all()
        return [ModeloResponse.model_validate(m) for m in modelos]
    
    async def update_modelo(self, modelo_id: UUID, modelo_data: ModeloUpdate) -> Optional[ModeloResponse]:
        """Actualizar un modelo."""
        result = await self.db.execute(
            select(ModeloNeumatico).where(ModeloNeumatico.id == modelo_id)
        )
        modelo = result.scalar_one_or_none()
        if not modelo:
            return None
        
        update_data = modelo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(modelo, field, value)
        
        await self.db.commit()
        await self.db.refresh(modelo)
        return ModeloResponse.model_validate(modelo)
    
    async def delete_modelo(self, modelo_id: UUID) -> bool:
        """Eliminar un modelo."""
        result = await self.db.execute(
            select(ModeloNeumatico).where(ModeloNeumatico.id == modelo_id)
        )
        modelo = result.scalar_one_or_none()
        if not modelo:
            return False
        
        await self.db.delete(modelo)
        await self.db.commit()
        return True
