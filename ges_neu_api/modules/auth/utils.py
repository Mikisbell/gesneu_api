"""
Utilidades para autenticación y manejo de contraseñas.
"""
from passlib.context import CryptContext
from typing import cast

# Configuración del contexto de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Genera un hash de la contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    return cast(bool, pwd_context.verify(plain_password, hashed_password))
