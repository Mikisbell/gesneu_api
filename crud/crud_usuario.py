# crud/crud_usuario.py
from typing import Any, Dict, Union, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select # <--- IMPORTACIÓN AÑADIDA AQUÍ

from crud.base import CRUDBase
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, UsuarioUpdate # Asegúrate que este archivo exista y sea correcto
from core.security import get_password_hash

class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    async def create(self, session: AsyncSession, *, obj_in: UsuarioCreate) -> Usuario:
        """
        Create a new user with hashed password.

        Args:
            session: The database session.
            obj_in: The schema containing the user data.

        Returns:
            The created user instance.
        """
        # Hash the password before creating the user
        hashed_password = get_password_hash(obj_in.password)
        # Create a dictionary from the input object, excluding the plain password
        # For Pydantic V2, model_dump() is the successor to dict()
        obj_in_data = obj_in.model_dump(exclude={"password"}) 
        # Add the hashed password to the data
        db_obj = self.model(**obj_in_data, hashed_password=hashed_password)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: Usuario,
        obj_in: Union[UsuarioUpdate, Dict[str, Any]]
    ) -> Usuario:
        """
        Update an existing user, optionally hashing the new password.

        Args:
            session: The database session.
            db_obj: The existing user instance to update.
            obj_in: The schema or dictionary containing the update data.

        Returns:
            The updated user instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # For Pydantic V2, model_dump() is the successor to dict()
            update_data = obj_in.model_dump(exclude_unset=True) 

        # If password is in update data, hash it
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"] # Remove plain password from update data

        # Call the superclass update method
        return await super().update(session, db_obj=db_obj, obj_in=update_data)

    async def get_by_email(self, session: AsyncSession, *, email: str) -> Optional[Usuario]:
        """
        Retrieve a user by their email address.

        Args:
            session: The database session.
            email: The email address of the user to retrieve.

        Returns:
            The user instance if found, otherwise None.
        """
        # Construct the select statement
        statement = select(Usuario).where(Usuario.email == email)
        # Execute the statement
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_username(self, session: AsyncSession, *, username: str) -> Optional[Usuario]:
        """
        Retrieve a user by their username.

        Args:
            session: The database session.
            username: The username of the user to retrieve.

        Returns:
            The user instance if found, otherwise None.
        """
        # Construct the select statement
        statement = select(Usuario).where(Usuario.username == username)
        # Execute the statement
        result = await session.execute(statement)
        return result.scalar_one_or_none()

# Instance of the CRUD class for Usuario
usuario = CRUDUsuario(Usuario)
