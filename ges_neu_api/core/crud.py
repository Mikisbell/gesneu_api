"""
Base CRUD operations for all modules.
"""
from typing import Optional, List, Type, Dict, Any, TypeVar, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)

class CRUDBase:
    """Base CRUD class for database operations with AsyncSession."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: Union[Dict[str, Any], Any]) -> ModelType:
        """Create a new record."""
        # Ensure we have an AsyncSession
        if not isinstance(db, AsyncSession):
            raise TypeError(f"Expected AsyncSession, got {type(db)}")
            
        # Handle different input types
        if isinstance(obj_in, dict):
            obj_data = obj_in
        elif hasattr(obj_in, 'dict'):
            obj_data = obj_in.dict()
        elif hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump()
        else:
            obj_data = obj_in
            
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update an existing record."""
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> Optional[UUID]:
        """Delete a record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return id
        return None
