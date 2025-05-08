from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: A SQLModel model class
        """
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.

        Args:
            session: The database session.
            id: The ID of the record to retrieve.

        Returns:
            The model instance if found, otherwise None.
        """
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Retrieve multiple records.

        Args:
            session: The database session.
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of model instances.
        """
        result = await session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            session: The database session.
            obj_in: The schema containing the data for the new record.

        Returns:
            The created model instance.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            session: The database session.
            db_obj: The existing model instance to update.
            obj_in: The schema or dictionary containing the update data.

        Returns:
            The updated model instance.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(self, session: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        Delete a record by its ID.

        Args:
            session: The database session.
            id: The ID of the record to delete.

        Returns:
            The deleted model instance if found, otherwise None.
        """
        result = await session.execute(select(self.model).where(self.model.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await session.delete(db_obj)
            await session.commit()
        return db_obj