# gesneu_api2/models/usuario.py
import uuid
from typing import Optional, List # Añadir List si se usa para relaciones
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import UUID as SQLAlchemyUUID, String # Importa el UUID genérico y String de SQLAlchemy
import sqlalchemy # Importar sqlalchemy para usar sqlalchemy.String
from .common import SQLModelTimestamp, EstadoItem # Asumiendo que SQLModelTimestamp está en common
from sqlmodel import Field

class UsuarioBase(SQLModel):
    username: str = Field(unique=True, index=True, max_length=50) # index=True aquí está bien (para Pydantic/SQLModel)
    email: str = Field(unique=True, index=True, max_length=100) # index=True aquí está bien
    nombre_completo: Optional[str] = Field(default=None, max_length=100)
    es_superusuario: bool = Field(default=False)
    # activo: bool = Field(default=True) # Se maneja con EstadoItem

class Usuario(UsuarioBase, SQLModelTimestamp, EstadoItem, table=True):
    __tablename__ = "usuarios"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        # primary_key=True, # Ya se movió a Column
        # index=True, # <--- ELIMINADO DE AQUÍ
        # nullable=False, # Ya se movió a Column
        sa_column=Column(
            SQLAlchemyUUID(as_uuid=True), 
            primary_key=True, 
            default=uuid.uuid4, # Default a nivel de BD
            unique=True, # Asegurar unicidad a nivel de BD
            nullable=False, # Nulabilidad a nivel de BD (implícito para PK)
            index=True # <--- index AHORA ESTÁ AQUÍ, DENTRO DE Column
        )
    )
 
    hashed_password: str = Field(
        sa_column=Column(sqlalchemy.String, nullable=False)
    )

    # Relaciones (ejemplos, ajustar según necesidad)
    # vehiculos_creados: List["Vehiculo"] = Relationship(back_populates="creador")
    # vehiculos_actualizados: List["Vehiculo"] = Relationship(back_populates="actualizador")
    # neumaticos_creados: List["Neumatico"] = Relationship(back_populates="creador")
    # neumaticos_actualizados: List["Neumatico"] = Relationship(back_populates="actualizador")

    class Config:
        from_attributes = True # Para Pydantic V2 (reemplaza orm_mode)
        # orm_mode = True # Para Pydantic V1
