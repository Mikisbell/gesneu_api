from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

# Removed jsonable_encoder import as it's deprecated with Pydantic v2
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
        # Using session.exec() instead of session.execute() to fix deprecation warning
        # session.exec() returns a different result type than session.execute()
        try:
            return await session.get(self.model, id)
        except Exception:
            # Fallback to query if direct get fails
            result = await session.exec(select(self.model).where(self.model.id == id))
            return result.first()

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
        # Using session.exec() instead of session.execute() to fix deprecation warning
        # session.exec() returns a different result type than session.execute()
        try:
            # Direct query with exec
            result = await session.exec(select(self.model).offset(skip).limit(limit))
            # Process results and handle both direct objects and tuples
            items = []
            for item in result:
                # Check if item is a tuple (which happens with certain SQLAlchemy queries)
                if isinstance(item, tuple):
                    # Extract the model instance from the tuple (usually first element)
                    if len(item) > 0 and isinstance(item[0], self.model):
                        items.append(item[0])
                else:
                    # Item is already a model instance
                    items.append(item)
            return items
        except Exception as e:
            print(f"Error in get_multi: {e}")
            # Fallback to execute approach if exec fails
            try:
                # Legacy approach with execute
                result = await session.execute(select(self.model).offset(skip).limit(limit))
                return list(result.scalars().all())
            except Exception as e2:
                print(f"Error in get_multi fallback: {e2}")
                return []

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            session: The database session.
            obj_in: The schema containing the data for the new record.

        Returns:
            The created model instance.
        """
        # Using model_dump instead of jsonable_encoder for Pydantic v2 compatibility
        obj_in_data = obj_in.model_dump()
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
        # Using model_dump instead of jsonable_encoder for Pydantic v2 compatibility
        obj_data = db_obj.model_dump() if hasattr(db_obj, 'model_dump') else {k: v for k, v in db_obj.__dict__.items() if not k.startswith('_')}
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
        # Using session.exec() instead of session.execute() to fix deprecation warning
        # First try to get the object directly
        try:
            db_obj = await session.get(self.model, id)
            if db_obj:
                await session.delete(db_obj)
                await session.commit()
            return db_obj
        except Exception:
            # Fallback to query if direct get fails
            result = await session.exec(select(self.model).where(self.model.id == id))
            db_obj = result.first()
            if db_obj:
                await session.delete(db_obj)
                await session.commit()
            return db_obj