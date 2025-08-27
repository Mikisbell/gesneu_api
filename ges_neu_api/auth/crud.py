#ges_neu_api/ges_neu_api/auth/crud.py

from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .schemas import UsuarioCreate

# Importación condicional para evitar dependencias circulares
if TYPE_CHECKING:
    from .models.usuario import Usuario

class CRUDUsuario:
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional["Usuario"]:
        """
        Busca un usuario por su nombre de usuario.
        """
        from .models.usuario import Usuario  # Importación local
        statement = select(Usuario).where(Usuario.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UsuarioCreate, password_hash: str) -> "Usuario":
        """
        Crea un nuevo usuario en la base de datos.
        """
        from .models.usuario import Usuario  # Importación local
        # Creamos un diccionario a partir del schema, excluyendo la contraseña en texto plano
        db_obj_data = obj_in.dict(exclude={"password"})
        # Creamos el objeto del modelo de base de datos
        db_obj = Usuario(**db_obj_data, password_hash=password_hash)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

# Creamos una instancia para usarla en otros archivos
crud_usuario = CRUDUsuario()