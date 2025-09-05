"""Test data factories for the catalogos module."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.modules.catalogos import models as catalogos_models
from tests.factories import ModelFactory


class FabricanteFactory(ModelFactory):
    """Factory for creating Fabricante test data."""

    @classmethod
    def build(
        cls,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        activo: bool = True,
        creado_por: Optional[str] = None,
        **overrides: Any
    ) -> Dict[str, Any]:
        """Build a fabricante dictionary."""
        uid = str(uuid4())
        return {
            "id": str(uuid4()),
            "nombre": nombre or f"Fabricante-{uid[:8]}",
            "descripcion": descripcion or f"Descripción del fabricante {uid[:8]}",
            "activo": activo,
            "fecha_creacion": datetime.now(timezone.utc),
            "creado_por": creado_por or "system",
            **overrides
        }

    @classmethod
    async def create(
        cls, 
        db: AsyncSession, 
        **overrides: Any
    ) -> catalogos_models.Fabricante:
        """Create and persist a fabricante."""
        data = cls.build(**overrides)
        fabricante = catalogos_models.Fabricante(**data)
        db.add(fabricante)
        await db.commit()
        await db.refresh(fabricante)
        return fabricante
