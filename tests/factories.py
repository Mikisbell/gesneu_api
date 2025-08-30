"""Test data factories for the test suite."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, TypeVar
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.modules.auth.models import Usuario, UsuariosRoles
from ges_neu_api.catalogos import models as catalogos_models
from ges_neu_api.modules.catalogos import schemas as catalogos_schemas

T = TypeVar('T')

class ModelFactory:
    """Base factory for creating test model instances."""
    
    @classmethod
    def build(cls, **overrides: Any) -> Dict[str, Any]:
        """Build a dictionary of model attributes."""
        raise NotImplementedError
    
    @classmethod
    def create(cls, db: AsyncSession, **overrides: Any) -> Any:
        """Create and persist a model instance."""
        raise NotImplementedError
    
    @classmethod
    def create_batch(
        cls, 
        db: AsyncSession, 
        size: int, 
        **overrides: Any
    ) -> list[Any]:
        """Create a batch of model instances."""
        return [cls.create(db, **overrides) for _ in range(size)]


class UsuarioFactory(ModelFactory):
    """Factory for creating Usuario test data."""
    
    @classmethod
    def build(
        cls, 
        email: Optional[str] = None,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        rol: Optional[UsuariosRoles] = None,
        activo: bool = True,
        **overrides: Any
    ) -> Dict[str, Any]:
        """Build a user dictionary."""
        uid = str(uuid4())
        return {
            "id": uid,
            "email": email or f"user-{uid[:8]}@example.com",
            "nombre": nombre or f"User-{uid[:4]}",
            "apellido": apellido or f"Test-{uid[4:8]}",
            "hashed_password": f"hashed_password_{uid}",
            "rol": rol or RolUsuario.USUARIO,
            "activo": activo,
            "fecha_creacion": datetime.now(timezone.utc),
            "creado_por": "system",
            **overrides
        }
    
    @classmethod
    async def create(
        cls, 
        db: AsyncSession, 
        **overrides: Any
    ) -> Usuario:
        """Create and persist a user."""
        data = cls.build(**overrides)
        user = Usuario(**data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


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






