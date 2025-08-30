"""Add vehiculos and posiciones_vehiculo tables

Revision ID: YYYYMMDD_HHMM
Revises: 7b924ead673c
Create Date: 2025-08-25 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'YYYYMMDD_HHMM'
down_revision: Union[str, None] = '7b924ead673c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create posiciones_vehiculo table
    op.create_table(
        'posiciones_vehiculo',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('codigo', sa.String(length=10), nullable=False, unique=True, index=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='public',
        comment='Define las posiciones de neumáticos en un vehículo'
    )

    # Create vehiculos table
    op.create_table(
        'vehiculos',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('placa', sa.String(length=20), nullable=False, unique=True, index=True),
        sa.Column('numero_economico', sa.String(length=50), nullable=True, unique=True, index=True),
        sa.Column('marca', sa.String(length=100), nullable=True),
        sa.Column('modelo', sa.String(length=100), nullable=True),
        sa.Column('anio', sa.Integer(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('creado_por', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['creado_por'], ['public.usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='public',
        comment='Almacena información sobre los vehículos de la flota'
    )

    # Create posiciones_historico table
    op.create_table(
        'posiciones_historico',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('neumatico_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('posicion_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('fecha_instalacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_remocion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('odometro_instalacion', sa.Integer(), nullable=True),
        sa.Column('odometro_remocion', sa.Integer(), nullable=True),
        sa.Column('motivo_remocion', sa.Text(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('creado_por', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['creado_por'], ['public.usuarios.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['neumatico_id'], ['public.neumaticos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['posicion_id'], ['public.posiciones_vehiculo.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['public.vehiculos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='public',
        comment='Historial de posiciones de los neumáticos en vehículos'
    )

def downgrade() -> None:
    op.drop_table('posiciones_historico', schema='public')
    op.drop_table('vehiculos', schema='public')
    op.drop_table('posiciones_vehiculo', schema='public')
