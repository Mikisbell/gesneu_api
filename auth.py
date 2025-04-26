# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError # Importar JWTError para manejar errores de token
from sqlmodel import select # Importar select de SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession # Importar AsyncSession

# Tus imports existentes
from core.security import verify_token
from database import get_session # Necesitamos la sesión de BD
from models.usuario import Usuario # Necesitamos el modelo Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") # Asumiendo que tu endpoint de token está en /auth/token

# --- Función get_current_user Modificada ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session) # <-- Inyectar sesión de BD
) -> Usuario: # <-- Especificar que devuelve un objeto Usuario
    """
    Verifica el token JWT, obtiene el username y devuelve el objeto Usuario completo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Verificar el token y obtener el payload (diccionario)
        payload = verify_token(token)
        username: str | None = payload.get("sub") # "sub" es el campo estándar para el sujeto (username)
        if username is None:
            # Si el token no tiene el campo 'sub' (username), es inválido
            raise credentials_exception

        # 2. Buscar el usuario en la base de datos usando el username
        statement = select(Usuario).where(Usuario.username == username)
        # ¡Usar exec() porque ahora get_session devuelve una sesión SQLModel!
        results = await session.exec(statement)
        user = results.first()

        if user is None:
            # Si el usuario extraído del token ya no existe en la BD
            raise credentials_exception

        # 3. Devolver el objeto Usuario completo
        return user

    except JWTError:
        # Si verify_token falla (token expirado, firma inválida, etc.)
        raise credentials_exception
    except Exception as e:
        # Capturar otros posibles errores durante la obtención del usuario
        # Podrías loggear 'e' aquí
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication.",
        )

# --- (Opcional) Añadir get_current_active_user si lo necesitas ---
# Si tienes un campo 'activo' en tu modelo Usuario y quieres asegurarte
# de que solo usuarios activos puedan operar:
async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user) # Depende de get_current_user
) -> Usuario:
    if not current_user.activo: # Asumiendo que tienes un campo booleano 'activo'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user