#!/usr/bin/env python3
"""
Script simple para corregir modelos usando ESQUEMA_COMPLETO_BD.md
Enfoque directo: extraer info de tablas críticas y generar modelos correctos
"""

def create_alertas_model():
    """Genera modelo Alertas basado en esquema real"""
    return '''from datetime import datetime
from typing import Optional, Dict
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, JSONB, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class Alertas(SQLModel, table=True):
    """Modelo para tabla alertas - Alineado exactamente con esquema real"""
    __tablename__ = "alertas"

    # Campos exactos del esquema PostgreSQL
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    tipo_alerta: str = Field(sa_column=Column(String(50), nullable=False))
    mensaje: str = Field(sa_column=Column(Text, nullable=False))
    nivel_severidad: str = Field(default='INFO', sa_column=Column(String(20), nullable=False))
    estado_alerta: str = Field(default='NUEVA', sa_column=Column(String(20), nullable=False))
    timestamp_generacion: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    timestamp_gestion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    usuario_gestion_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    neumatico_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    modelo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    parametro_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    datos_contexto: Optional[Dict] = Field(default=None, sa_column=Column(JSONB))
'''

def create_neumaticos_model():
    """Genera modelo Neumaticos basado en esquema real"""
    return '''from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, Date, Numeric, Boolean, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class Neumaticos(SQLModel, table=True):
    """Modelo para tabla neumaticos - Alineado exactamente con esquema real"""
    __tablename__ = "neumaticos"

    # Campos exactos del esquema PostgreSQL
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    numero_serie: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False))
    proveedor_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    posicion_neumatico_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    estado_neumatico: str = Field(default='EN_STOCK', sa_column=Column(String(20), nullable=False))
    fecha_compra: Optional[date] = Field(default=None, sa_column=Column(Date))
    fecha_instalacion: Optional[date] = Field(default=None, sa_column=Column(Date))
    fecha_desmontaje: Optional[date] = Field(default=None, sa_column=Column(Date))
    kilometraje_instalacion: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    kilometraje_desmontaje: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    profundidad_actual_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    presion_recomendada_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    presion_actual_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    numero_reencauches: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    numero_reparaciones: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    costo_compra: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
'''

def create_usuarios_model():
    """Genera modelo Usuarios basado en esquema real"""
    return '''from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class Usuario(SQLModel, table=True):
    """Modelo para tabla usuarios - Alineado exactamente con esquema real"""
    __tablename__ = "usuarios"

    # Campos exactos del esquema PostgreSQL
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    username: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    email: Optional[str] = Field(default=None, sa_column=Column(String(100), unique=True))
    password_hash: Optional[str] = Field(default=None, sa_column=Column(Text))
    nombre_completo: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    ultimo_login: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
'''

def main():
    """Genera modelos corregidos para módulos críticos"""
    print("🔧 GENERANDO MODELOS CORREGIDOS DESDE ESQUEMA COMPLETO")
    print("="*60)
    
    # Crear directorio para modelos corregidos
    from pathlib import Path
    
    # Modelo Alertas
    alertas_dir = Path("ges_neu_api/modules/alertas")
    alertas_dir.mkdir(parents=True, exist_ok=True)
    
    with open(alertas_dir / "models_fixed.py", 'w', encoding='utf-8') as f:
        f.write(create_alertas_model())
    print("✅ Modelo Alertas corregido: ges_neu_api/modules/alertas/models_fixed.py")
    
    # Modelo Neumaticos
    neumaticos_dir = Path("ges_neu_api/modules/neumaticos")
    neumaticos_dir.mkdir(parents=True, exist_ok=True)
    
    with open(neumaticos_dir / "models_fixed.py", 'w', encoding='utf-8') as f:
        f.write(create_neumaticos_model())
    print("✅ Modelo Neumaticos corregido: ges_neu_api/modules/neumaticos/models_fixed.py")
    
    # Modelo Usuarios
    auth_dir = Path("ges_neu_api/modules/auth")
    auth_dir.mkdir(parents=True, exist_ok=True)
    
    with open(auth_dir / "models_fixed.py", 'w', encoding='utf-8') as f:
        f.write(create_usuarios_model())
    print("✅ Modelo Usuario corregido: ges_neu_api/modules/auth/models_fixed.py")
    
    print("\n" + "="*60)
    print("🎉 MODELOS CRÍTICOS CORREGIDOS")
    print("\n📋 Archivos generados:")
    print("  • ges_neu_api/modules/alertas/models_fixed.py")
    print("  • ges_neu_api/modules/neumaticos/models_fixed.py") 
    print("  • ges_neu_api/modules/auth/models_fixed.py")
    
    print("\n⚠️  PRÓXIMOS PASOS:")
    print("  1. Reemplazar imports en servicios para usar models_fixed")
    print("  2. Probar que la API arranca sin errores")
    print("  3. Validar autenticación y endpoints críticos")
    print("  4. Aplicar mismo patrón a resto de modelos")

if __name__ == "__main__":
    main()
