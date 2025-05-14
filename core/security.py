# core/security.py
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from core.config import settings
import warnings

# Suprimir warnings específicos de passlib
warnings.filterwarnings("ignore", ".*trapped.*error reading bcrypt version.*")

# --- Añadir importaciones para passlib ---
from passlib.context import CryptContext

# --- Crear instancia del contexto ---
# Le decimos que use bcrypt como esquema por defecto
# y que marque otros hashes como obsoletos automáticamente si los encontrara
# Configuración optimizada para evitar warnings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Número de rondas para bcrypt
    bcrypt__ident="2b"  # Usar formato $2b$ (más compatible)
)

# --- Funciones Helper para Contraseñas ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra un hash existente."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña plana."""
    return pwd_context.hash(password)

# --- Funciones de Token (las que ya tenías) ---
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def verify_token(token: str) -> dict:
    try:
        # Primero decodifica, la validación de expiración la hace jwt.decode
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        # Podrías añadir validaciones extra al payload aquí si quisieras
        return payload
    except JWTError as e:
        # Loggear el error puede ser útil: print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials", # Mensaje genérico
            headers={"WWW-Authenticate": "Bearer"},
        )