from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel, Field
from ges_neu_api.core.base_models import BaseModel

class Neumatico(BaseModel, table=True):
    __tablename__ = "neumaticos"
    
    # Basic fields only
    modelo_id: UUID = Field(foreign_key="public.modelos_neumatico.id", nullable=False, index=True)
    numero_serie: Optional[str] = Field(default=None, max_length=100, unique=True, index=True)
    
    # Minimal required fields
    estado_actual: str = Field(default="EN_STOCK", nullable=False)
    
    # Simple fields without complex configurations
    costo_compra: Optional[Decimal] = None
    fecha_compra: Optional[date] = None
    fecha_fabricacion: Optional[date] = None
    
    class Config:
        arbitrary_types_allowed = True