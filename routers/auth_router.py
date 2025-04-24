# routers/auth_router.py (Corregido para Refactorización v3)
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession # type: ignore

# --- Importaciones Corregidas ---
import auth                             # Módulo local con lógica de auth
from database import get_session      # Dependencia de sesión de BD
# Modelos específicos de sus nuevas ubicaciones:
from models.usuario import Usuario     # Modelo de TABLA Usuario
from schemas.token import Token       # Schema de API para la respuesta del Token
# --- Fin Importaciones Corregidas ---


router = APIRouter(tags=["Autenticación"])

@router.post("/token", response_model=Token) # <-- Usa Token importado
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Endpoint para login. Recibe username y password en form data.
    Verifica credenciales y retorna un token JWT.
    """
    # Llama a la función en auth.py, que usa/devuelve el modelo Usuario
    user = await auth.get_user(session, form_data.username)

    if not user or not user.password_hash or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # print(f"DEBUG: Diccionario a retornar: {{'access_token': access_token, 'token_type': 'bearer'}}") # Mantener si se quiere depurar

    return {"access_token": access_token, "token_type": "bearer"}