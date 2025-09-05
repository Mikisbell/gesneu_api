"""Test data factories for the test suite."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, TypeVar
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any, Dict, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class ModelFactory(Generic[T]):
    """Base factory for creating test model instances."""

    @classmethod
    def build(cls, **overrides: Any) -> Dict[str, Any]:
        """Build a dictionary of model attributes."""
        raise NotImplementedError

    @classmethod
    async def create(cls, db: AsyncSession, **overrides: Any) -> T:
        """Create and persist a model instance."""
        raise NotImplementedError

    @classmethod
    async def create_batch(
        cls, 
        db: AsyncSession, 
        size: int, 
        **overrides: Any
    ) -> list[T]:
        """Create a batch of model instances."""
        return [await cls.create(db, **overrides) for _ in range(size)]






