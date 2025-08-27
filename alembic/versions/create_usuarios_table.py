"""Create usuarios table

Revision ID: 1234567890ab
Revises: 7b924ead673c
Create Date: 2025-08-23 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1234567890ab'
down_revision: str = '7b924ead673c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'usuarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('username', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('nombre_completo', sa.String(200), nullable=True),
        sa.Column('email', sa.String(100), unique=True, index=True, nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('activo', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('ultimo_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('creado_por', postgresql.UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('now()')),
        sa.Column('actualizado_por', postgresql.UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=True),
    )
    
    # Create admin user
    op.execute("""
        INSERT INTO usuarios (id, username, nombre_completo, email, password_hash, activo)
        VALUES (
            '11111111-1111-1111-1111-111111111111',
            'admin',
            'Administrador del Sistema',
            'admin@example.com',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- password: admin123
            true
        )
    """)

def downgrade() -> None:
    op.drop_table('usuarios')
