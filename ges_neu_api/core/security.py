# ges_neu_api/ges_neu_api/core/security.py

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, cast

from passlib.context import CryptContext
from jose import JWTError, jwt

# Importamos nuestra configuración
from .config import settings

# Configuración de logging
logger = logging.getLogger(__name__)

# Configuración de hash de contraseñas
# Configuración actualizada para evitar warnings de passlib
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # Especificar rounds explícitamente
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con una hasheada.
    """
    try:
        is_valid = cast(bool, pwd_context.verify(plain_password, hashed_password))
        if not is_valid:
            logger.warning("La contraseña proporcionada no coincide con el hash almacenado")
        return is_valid
    except Exception as e:
        logger.error(f"Error al verificar la contraseña: {str(e)}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    """
    Convierte una contraseña en texto plano a un hash seguro.
    """
    try:
        return cast(str, pwd_context.hash(password))
    except Exception as e:
        logger.error(f"Error al hashear la contraseña: {str(e)}", exc_info=True)
        raise ValueError("No se pudo hashear la contraseña") from e

def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un nuevo token de acceso (JWT).
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # Si no se especifica tiempo, usamos el de la configuración (30 min)
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        
        # Validar que tenemos los datos necesarios
        if not settings.jwt_secret_key:
            logger.error("JWT_SECRET_KEY no está configurada")
            raise ValueError("JWT_SECRET_KEY no está configurada")
            
        if not settings.jwt_algorithm:
            logger.error("JWT_ALGORITHM no está configurado")
            raise ValueError("JWT_ALGORITHM no está configurado")
        
        # Usamos nuestra JWT_SECRET_KEY y JWT_ALGORITHM del archivo .env para firmar el token
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        
        logger.debug(f"Token JWT generado exitosamente para el sujeto: {to_encode.get('sub')}")
        return cast(str, encoded_jwt)
        
    except JWTError as e:
        logger.error(f"Error JWT al crear token: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error inesperado al crear token: {str(e)}", exc_info=True)
        raise ValueError("No se pudo generar el token de acceso") from e

def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decodifica y valida un token JWT.
    """
    try:
        if not settings.jwt_secret_key:
            logger.error("JWT_SECRET_KEY no está configurada")
            raise ValueError("JWT_SECRET_KEY no está configurada")
            
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        
        logger.debug(f"Token JWT decodificado exitosamente para el sujeto: {payload.get('sub')}")
        return cast(dict[str, Any], payload)
        
    except JWTError as e:
        logger.warning(f"Error JWT al decodificar token: {str(e)}")
        raise ValueError("Token inválido o expirado") from e
    except Exception as e:
        logger.error(f"Error inesperado al decodificar token: {str(e)}", exc_info=True)
        raise ValueError("No se pudo decodificar el token") from e