# auth.py (Corregido para Refactorización v2)
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt # type: ignore
from passlib.context import CryptContext # type: ignore
from pydantic import ValidationError
from sqlmodel import select # type: ignore
from sqlmodel.ext.asyncio.session import AsyncSession # type: ignore

# --- Importaciones Corregidas ---
from database import get_session # Importar sesión de database local
from models.usuario import Usuario  # Importa el MODELO DE TABLA Usuario desde models/usuario.py
from schemas.token import TokenData # Importa el SCHEMA API TokenData desde schemas/token.py
# --- Fin Importaciones Corregidas ---


# Cargar variables de entorno
load_dotenv()

# --- Configuración ---
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_if_not_set") # Añadir un fallback o mejor validación
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

if not SECRET_KEY or SECRET_KEY == "fallback_secret_key_if_not_set":
    print("ADVERTENCIA: SECRET_KEY no configurada en .env. Usando valor inseguro.")
    # En producción, deberías lanzar un error: raise ValueError("SECRET_KEY no configurada")

# --- Contexto de Contraseña ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Esquema OAuth2 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") # Ajusta si tu endpoint de token tiene prefijo


# --- Funciones de Utilidad ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash."""
    if not hashed_password: return False
    try: return pwd_context.verify(plain_password, hashed_password)
    except Exception: return False # Ser más específico con la excepción si es posible

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT."""
    to_encode = data.copy()
    if expires_delta: expire = datetime.now(timezone.utc) + expires_delta
    else: expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(session: AsyncSession, username: str) -> Optional[Usuario]: # <-- Usa Usuario importado
    """Busca un usuario por username en la BD."""
    statement = select(Usuario).where(Usuario.username == username) # <-- Usa Usuario importado
    results = await session.exec(statement)
    return results.first()

# --- Dependencia de Autenticación ---

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: Annotated[AsyncSession, Depends(get_session)]) -> Usuario: # <-- Usa Usuario importado
    """
    Dependencia de FastAPI para obtener el usuario actual basado en el token JWT.
    Lanza HTTPException 401 si el token es inválido o el usuario no se encuentra.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None: raise credentials_exception
        token_data = TokenData(username=username) # <-- Usa TokenData importado
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await get_user(session, username=token_data.username) # Llama a get_user local
    if user is None: raise credentials_exception
    return user # Devuelve instancia de Usuario (tabla)

async def get_current_active_user(
    current_user: Annotated[Usuario, Depends(get_current_user)] # <-- Usa Usuario importado
) -> Usuario: # <-- Usa Usuario importado
    """
    Dependencia que usa get_current_user y además asegura que el usuario esté activo.
    """
    if not current_user.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user