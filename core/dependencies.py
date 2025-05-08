# gesneu_api2/core/dependencies.py
from typing import AsyncGenerator, Annotated  # Annotated para FastAPI más reciente
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import select

from database import AsyncSessionFactory
from core.config import settings
from core.security import verify_token
from models.usuario import Usuario # Asegúrate que tu modelo Usuario tenga el campo 'es_superusuario' y 'activo'

# Definir el esquema OAuth2
# Ajusta la URL según tu router de auth, por ejemplo, si es /api/v1/auth/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token") 

# Función para obtener la sesión de base de datos
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador asíncrono para obtener una sesión de base de datos.
    Maneja el commit y rollback automáticamente.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # El commit se podría manejar aquí si todas las operaciones de un request
            # deben ser parte de una única transacción gestionada por la dependencia.
            # Sin embargo, es más común hacer commit en los endpoints o CRUDs
            # después de operaciones de escritura exitosas.
            # await session.commit() 
        except Exception as e:
            print(f"ERROR en sesión: {e}. Haciendo rollback...")
            await session.rollback()
            raise
        finally:
            # La sesión se cierra automáticamente al salir del contexto 'async with'.
            pass

# Función para obtener el usuario actual a partir del token
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], # Usando Annotated para claridad
    session: Annotated[AsyncSession, Depends(get_session)]
) -> Usuario:
    """
    Verifica el token JWT, obtiene el username y devuelve el objeto Usuario completo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token) # verify_token debería decodificar y validar
        username: str | None = payload.get("sub") # "sub" es el campo estándar para el sujeto (username)
        if username is None:
            raise credentials_exception

        # Buscar el usuario en la base de datos usando el username
        # Usar session.exec() como recomienda SQLModel
        statement = select(Usuario).where(Usuario.username == username)
        db_user = await session.exec(statement)
        user = db_user.first() # .one_or_none() si quieres error si hay más de uno (aunque username es unique)

        if user is None:
            raise credentials_exception
        
        return user

    except JWTError: # Captura errores específicos de la decodificación/validación del JWT
        raise credentials_exception
    except Exception as e: # Captura otros posibles errores
        # Considera loggear el error 'e' aquí para depuración
        # print(f"Error inesperado en get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user retrieval.",
        )

# Función para obtener el usuario activo actual
async def get_current_active_user(
    current_user: Annotated[Usuario, Depends(get_current_user)]
) -> Usuario:
    """
    Dependencia para obtener el usuario actual que también está activo.
    """
    if not current_user.activo: # Asumiendo que tu modelo Usuario tiene un campo booleano 'activo'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# --- FUNCIÓN AÑADIDA ---
async def get_current_active_superuser(
    current_user: Annotated[Usuario, Depends(get_current_active_user)] # Depende del usuario activo
) -> Usuario:
    """
    Dependencia para obtener el usuario actual que está activo Y es superusuario.
    """
    if not hasattr(current_user, 'es_superusuario') or not current_user.es_superusuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    return current_user
