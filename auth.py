# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError # Importar JWTError para manejar errores de token
from sqlmodel import select # Importar select de SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession # Importar AsyncSession

# Tus imports existentes
from core.security import verify_token
from core.dependencies import get_session # Necesitamos la sesión de BD (importar desde dependencies)
from models.usuario import Usuario # Necesitamos el modelo Usuario
