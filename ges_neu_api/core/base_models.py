from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Type, TypeVar, Generic
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, ForeignKey, text, CheckConstraint, Integer, Numeric, String, Boolean, Date, DateTime, TIMESTAMP
from sqlalchemy.types import SmallInteger, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlmodel import SQLModel, Field

# Shared enums between models
class EstadoNeumaticoEnum(str, Enum):
    EN_STOCK = "EN_STOCK"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    EN_DESECHO = "EN_DESECHO"
    VENDIDO = "VENDIDO"
    PERDIDO = "PERDIDO"
    EN_TRANSITO = "EN_TRANSITO"
    EN_RECICLAJE = "EN_RECICLAJE"
    DESECHADO = "DESECHADO"

# Generic type for forward references
ModelType = TypeVar("ModelType", bound="BaseModel")

class BaseModel(SQLModel):
    """Base model with common fields and methods."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None,
        },
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2023-01-01T00:00:00",
            }
        },
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        ),
        description="Unique identifier"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default=text("true")
        ),
        description="Indicates if the record is active"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("now()")
        ),
        description="Creation timestamp"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("usuarios.id", ondelete="SET NULL")
        ),
        description="User who created the record"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP,
            onupdate=text("now()")
        ),
        description="Last update timestamp"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("usuarios.id", ondelete="SET NULL")
        ),
        description="User who last updated the record"
    )

# Helper function to handle SQLAlchemy types in Pydantic
def handle_sqlalchemy_type(field_type: Any) -> Any:
    """Handle SQLAlchemy types in Pydantic models."""
    if hasattr(field_type, "__origin__"):
        # Handle Optional types
        if field_type.__origin__ is not None and hasattr(field_type, "__args__"):
            return Optional[handle_sqlalchemy_type(field_type.__args__[0])]
        return field_type
    
    # Handle SQLAlchemy types
    if isinstance(field_type, (Date, DateTime)):
        return datetime if isinstance(field_type, DateTime) else date
    
    return field_type
