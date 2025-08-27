from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, Text, 
    CheckConstraint, UniqueConstraint, Index, Numeric, Date, SmallInteger,
    text, DDL, event, func, and_, or_, not_
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlmodel import SQLModel, Field, Relationship

# Import base model
from ges_neu_api.core.base_models import BaseModel

if TYPE_CHECKING:
    from ges_neu_api.catalogos.models import BitacoraOperacionNeumatico, ModeloVehiculo, PosicionNeumatico, BitacoraOperaciones
    from ges_neu_api.neumaticos.models import Neumatico
    from ges_neu_api.usuarios.models import Usuario
    from typing import List

class TipoVehiculo(SQLModel, table=True):
    __tablename__ = "tipos_vehiculo"
    __table_args__ = (
        {
            "schema": "public",
            "comment": "Tipos de vehículos disponibles en la flota",
        },
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del tipo de vehículo"
    )
    
    nombre: str = Field(
        sa_column=Column(String(100), nullable=False, index=True),
        description="Nombre del tipo de vehículo (ej: Camión, Torton, Tractocamión)"
    )
    
    descripcion: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Descripción detallada del tipo de vehículo"
    )
    
    categoria_principal: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Categoría principal del tipo de vehículo"
    )
    
    subtipo: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Subtipo específico del vehículo"
    )
    
    ejes_standard: int = Field(
        default=2,
        sa_column=Column(
            SmallInteger, 
            nullable=False, 
            server_default=text("2"),
            info={"check_constraint": "ejes_standard >= 1 AND ejes_standard <= 10"}
        ),
        description="Número estándar de ejes para este tipo de vehículo (1-10)"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el tipo de vehículo está activo"
    )
    
    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que realizó la última actualización"
    )
    
    # Relaciones
    vehiculos: List["Vehiculo"] = Relationship(back_populates="tipo_vehiculo")
    configuraciones_eje: List["ConfiguracionEje"] = Relationship(back_populates="tipo_vehiculo")


class Vehiculo(BaseModel, table=True):
    """Modelo para los vehículos del sistema."""
    __tablename__ = "vehiculos"
    __table_args__ = (
        {
            "schema": "public",
            "comment": "Registro de vehículos de la flota",
            "sqlite_autoincrement": True,
        },
        # Índices y restricciones adicionales
        Index("idx_vehiculos_activos", "activo"),
        Index("idx_vehiculos_numero_economico_ci", text("lower(numero_economico)")),
        Index("idx_vehiculos_placa_ci", text("lower(placa)")),
        Index("idx_vehiculos_vin_ci", text("lower(vin)")),
        Index("idx_vehiculos_tipo_estado", "tipo_vehiculo_id", "activo"),
        Index("idx_vehiculos_fechas_alta_baja", "fecha_alta", "fecha_baja"),
        Index("idx_vehiculos_marca_modelo", "marca", "modelo_vehiculo"),
        Index("idx_vehiculos_odometro", "odometro_actual"),
        # Restricciones CHECK
        CheckConstraint(
            "anio_fabricacion >= 1900 AND anio_fabricacion <= EXTRACT(year FROM CURRENT_DATE) + 1",
            name="vehiculos_anio_fabricacion_check"
        ),
        CheckConstraint(
            "fecha_baja IS NULL OR fecha_baja >= fecha_alta",
            name="vehiculos_fecha_baja_check"
        ),
        CheckConstraint(
            "odometro_actual IS NULL OR odometro_actual >= 0",
            name="vehiculos_odometro_actual_check"
        ),
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del vehículo"
    )
    
    tipo_vehiculo_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.tipos_vehiculo.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="ID del tipo de vehículo"
    )
    
    placa: Optional[str] = Field(
        default=None,
        sa_column=Column(String(10), unique=True, index=True),
        description="Placa o matrícula del vehículo"
    )
    
    vin: Optional[str] = Field(
        default=None,
        sa_column=Column(String(17), unique=True),
        description="Número de identificación del vehículo (VIN)"
    )
    
    numero_economico: str = Field(
        sa_column=Column(String(50), nullable=False, unique=True, index=True),
        description="Número económico asignado al vehículo"
    )
    
    marca: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Marca del vehículo"
    )
    
    modelo_vehiculo: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Modelo del vehículo"
    )
    
    anio_fabricacion: Optional[int] = Field(
        default=None,
        sa_column=Column(SmallInteger),
        description="Año de fabricación del vehículo"
    )
    
    fecha_alta: date = Field(
        default_factory=date.today,
        sa_column=Column(Date, nullable=False, server_default=text("CURRENT_DATE")),
        description="Fecha en que se dio de alta el vehículo en el sistema"
    )
    
    fecha_baja: Optional[date] = Field(
        default=None,
        sa_column=Column(Date),
        description="Fecha en que se dio de baja el vehículo"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el vehículo está activo"
    )
    
    odometro_actual: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer),
        description="Último registro de odómetro del vehículo"
    )
    
    fecha_ultimo_odometro: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha del último registro de odómetro"
    )
    
    ubicacion_actual: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100)),
        description="Ubicación actual del vehículo"
    )
    
    notas: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Notas adicionales sobre el vehículo"
    )
    
    peso_carga_maxima_diseno_ton: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Capacidad máxima de carga de diseño del vehículo en toneladas"
    )
    
    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que realizó la última actualización"
    )
    
    # Relaciones
    tipo_vehiculo: "TipoVehiculo" = Relationship(back_populates="vehiculos")
    
    # Relación con las operaciones de bitácora donde este vehículo está involucrado
    bitacora_operaciones: List["BitacoraOperaciones"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BitacoraOperaciones.vehiculo_id]"},
        back_populates="vehiculo"
    )
    
    # Relación con el usuario que creó el registro
    usuario_creador_rel: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Vehiculo.creado_por]"}
    )
    
    # Relación con el usuario que actualizó el registro
    usuario_actualizador_rel: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Vehiculo.actualizado_por]"}
    )
    
    # Relaciones con otras tablas (comentadas hasta que se definan los modelos)
    # alertas = Relationship("Alerta", back_populates="vehiculo")
    # eventos_neumaticos = Relationship("EventoNeumatico", back_populates="vehiculo")
    # neumaticos = Relationship("Neumatico", back_populates="ubicacion_actual_vehiculo")
    # registros_odometro = Relationship("RegistroOdometro", back_populates="vehiculo")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
        }

# Importaciones condicionales al final para evitar dependencias circulares
if not TYPE_CHECKING:
    from ges_neu_api.catalogos.models import ModeloVehiculo, PosicionNeumatico, BitacoraOperaciones
    from ges_neu_api.neumaticos.models import Neumatico
    from ges_neu_api.usuarios.models import Usuario


class ConfiguracionEje(BaseModel, table=True):
    __tablename__ = "configuraciones_eje"
    __table_args__ = (
        {
            "schema": "public",
            "comment": "Configuraciones de ejes para tipos de vehículos",
            "sqlite_autoincrement": True,
            "postgresql_with": {"fillfactor": "90"}
        },
        # Restricción única compuesta
        UniqueConstraint("tipo_vehiculo_id", "numero_eje", name="uq_configuracion_eje"),
        # Restricciones CHECK
        CheckConstraint("numero_eje > 0", name="configuraciones_eje_numero_eje_check"),
        CheckConstraint(
            "numero_posiciones >= 1 AND numero_posiciones <= 6",
            name="configuraciones_eje_numero_posiciones_check"
        ),
        CheckConstraint(
            "neumaticos_por_posicion = ANY (ARRAY[1, 2])",
            name="configuraciones_eje_neumaticos_por_posicion_check"
        )
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único de la configuración de eje"
    )
    
    tipo_vehiculo_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.tipos_vehiculo.id", ondelete="CASCADE"),
            nullable=False
        ),
        description="ID del tipo de vehículo"
    )
    
    numero_eje: int = Field(
        sa_column=Column(SmallInteger, nullable=False),
        description="Número secuencial del eje en el vehículo"
    )
    
    nombre_eje: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="Nombre descriptivo del eje"
    )
    
    tipo_eje: str = Field(
        sa_column=Column(String(20), nullable=False),  
        description="Tipo de eje (delantero, trasero, direccional, etc.)"
    )
    
    numero_posiciones: int = Field(
        sa_column=Column(SmallInteger, nullable=False),
        description="Número de posiciones de neumáticos en el eje"
    )
    
    posiciones_duales: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si el eje tiene posiciones dobles"
    )
    
    permite_reencauchados: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si se permiten neumáticos reencauchados en este eje"
    )
    
    neumaticos_por_posicion: int = Field(
        default=1,
        sa_column=Column(SmallInteger, nullable=False, server_default=text("1")),
        description="Número de neumáticos por posición (1 o 2)"
    )
    
    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que realizó la última actualización"
    )
    
    # Relaciones
    tipo_vehiculo: "TipoVehiculo" = Relationship(back_populates="configuraciones_eje")
    posiciones: List["PosicionNeumatico"] = Relationship(back_populates="configuracion_eje")

    # Validaciones de negocio
    @validator('tipo_eje')
    def validar_tipo_eje(cls, v):
        tipos_validos = ["delantero", "trasero", "direccional", "arrastre", "elevable"]
        if v.lower() not in tipos_validos:
            raise ValueError(f"Tipo de eje no válido. Debe ser uno de: {', '.join(tipos_validos)}")
        return v.lower()
    
    @validator('neumaticos_por_posicion')
    def validar_neumaticos_por_posicion(cls, v, values):
        if 'posiciones_duales' in values and values['posiciones_duales'] and v != 1:
            raise ValueError("Las posiciones dobles solo pueden tener un neumático por posición")
        return v
    
    @validator('numero_posiciones')
    def validar_numero_posiciones(cls, v, values):
        if v > 2 and 'tipo_eje' in values and values['tipo_eje'] == 'direccional':
            raise ValueError("Los ejes direccionales no pueden tener más de 2 posiciones")
        return v
    
    # Métodos de negocio
    def puede_aceptar_neumatico(self, neumatico: 'Neumatico') -> bool:
        """
        Determina si un neumático puede ser montado en este eje.
        
        Args:
            neumatico: Instancia del neumático a validar
            
        Returns:
            bool: True si el neumático puede ser montado, False en caso contrario
        """
        # Validar si el neumático es reencauchado y el eje lo permite
        if neumatico.es_reencauchado and not self.permite_reencauchados:
            return False
            
        # Aquí podrías agregar más validaciones específicas
        # como medidas, tipo de neumático, etc.
        
        return True
    
    def obtener_posiciones_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene las posiciones disponibles en el eje.
        
        Returns:
            List[Dict]: Lista de diccionarios con información de las posiciones
        """
        from ges_neu_api.catalogos.models import PosicionNeumatico
        
        posiciones = []
        for i in range(1, self.numero_posiciones + 1):
            # Verificar si la posición ya está ocupada
            posicion_ocupada = any(
                p for p in self.posiciones 
                if p.posicion_relativa == i
            )
            
            if not posicion_ocupada:
                posiciones.append({
                    'posicion_relativa': i,
                    'es_interna': False,
                    'es_direccion': self.tipo_eje == 'direccional',
                    'es_traccion': self.tipo_eje in ['trasero', 'arrastre']
                })
                
                # Si es posición dual, agregar posición interna
                if self.posiciones_duales:
                    posiciones.append({
                        'posicion_relativa': i,
                        'es_interna': True,
                        'es_direccion': False,
                        'es_traccion': self.tipo_eje in ['trasero', 'arrastre']
                    })
        
        return posiciones


class PosicionNeumatico(SQLModel, table=True):
    __tablename__ = "posiciones_neumatico"
    __table_args__ = (
        {
            "schema": "public",
            "comment": "Define las posiciones de neumáticos en los ejes de los vehículos",
            "sqlite_autoincrement": True,
        },
        # Restricción única compuesta
        UniqueConstraint("configuracion_eje_id", "codigo_posicion", name="uq_posicion_neumatico"),
        # Restricción CHECK
        CheckConstraint("posicion_relativa > 0", name="posiciones_neumatico_posicion_relativa_check")
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único de la posición de neumático"
    )
    
    configuracion_eje_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.configuraciones_eje.id", ondelete="CASCADE"),
            nullable=False
        ),
        description="ID de la configuración de eje a la que pertenece esta posición"
    )
    
    codigo_posicion: str = Field(
        sa_column=Column(String(10), nullable=False),
        description="Código único de la posición dentro de la configuración de eje"
    )
    
    etiqueta_posicion: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Etiqueta descriptiva de la posición"
    )
    
    lado: str = Field(
        sa_column=Column(String(20), nullable=False),  
        description="Lado del vehículo donde se encuentra la posición"
    )
    
    posicion_relativa: int = Field(
        sa_column=Column(SmallInteger, nullable=False),
        description="Posición relativa del neumático en el eje"
    )
    
    es_interna: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si es una posición interna (doble neumático)"
    )
    
    es_direccion: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si es una posición de dirección"
    )
    
    es_traccion: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si es una posición de tracción"
    )
    
    requiere_neumatico_especifico: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si esta posición requiere un neumático específico"
    )
    
    # Relaciones
    configuracion_eje: "ConfiguracionEje" = Relationship(back_populates="posiciones")
    
    # Relación con BitacoraOperacionNeumatico
    bitacora_operaciones: List["BitacoraOperacionNeumatico"] = Relationship(
        back_populates="posicion_neumatico",
        sa_relationship_kwargs={
            "foreign_keys": "BitacoraOperacionNeumatico.posicion_neumatico_id"
        }
    )
    
    # Relaciones con otras tablas (comentadas hasta que se definan los modelos)
    # eventos = Relationship("EventoNeumatico", back_populates="posicion")
    # modelos_posiciones_permitidas = Relationship("ModeloPosicionPermitida", back_populates="posicion_neumatico")
    
    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL")
        ),
        description="ID del usuario que realizó la última actualización"
    )
