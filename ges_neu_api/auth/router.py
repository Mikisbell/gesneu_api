"""
Router para la autenticación y gestión de usuarios.

Este módulo define los endpoints relacionados con la autenticación
y gestión de usuarios, utilizando los servicios inyectados.
"""
from datetime import timedelta, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import get_session
from .schemas import Token, UsuarioCreate, UsuarioRead
from .service import AuthService, UserService, get_current_user
from .dependencies import CurrentAuthService, get_auth_service
from .models.usuario import Usuario

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token, summary="Obtener token de acceso")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    Obtén un token de acceso para las credenciales proporcionadas.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    """
    access_token = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/usuarios/me/", 
    response_model=UsuarioRead,
    summary="Obtener información del usuario actual"
)
async def read_users_me(
    current_user: Usuario = Depends(get_current_user)
) -> UsuarioRead:
    """
    Obtiene la información del usuario actualmente autenticado.
    
    Requiere autenticación con un token JWT válido.
    """
    return current_user

@router.post(
    "/usuarios/", 
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario"
)
async def create_user(
    user: UsuarioCreate,
    user_service: UserService = Depends(lambda: UserService(db=get_session()))
) -> UsuarioRead:
    """
    Crea un nuevo usuario.
    
    - **username**: Nombre de usuario único
    - **email**: Correo electrónico
    - **password**: Contraseña
    - **nombre**: Nombre del usuario (opcional)
    - **apellido**: Apellido del usuario (opcional)
    """
    # Verificar si el usuario ya existe
    existing_user = await user_service.get_user_by_username(username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado.",
        )
    
    # Verificar si el email ya está en uso
    if user.email:
        existing_email = await get_session().execute(
            select(Usuario).where(Usuario.email == user.email)
        )
        if existing_email.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado.",
            )
    
    # Crear el diccionario de datos del usuario
    user_data = user.dict()
    
    try:
        # Crear el usuario usando el servicio
        db_user = await user_service.create_user(user_data)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el usuario"
        )
