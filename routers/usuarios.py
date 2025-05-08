# gesneu_api2/routers/usuarios.py
import uuid # <--- IMPORTACIÓN AÑADIDA
from datetime import datetime # <--- IMPORTACIÓN AÑADIDA
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from crud.crud_usuario import usuario as crud_usuario
from schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate
from models.usuario import Usuario as ModelUsuario
from core.dependencies import get_session, get_current_active_user, get_current_active_superuser
from core.config import settings # Para el prefijo de la API
from utils.logging import logger

router = APIRouter()

@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario_endpoint(
    *,
    session: AsyncSession = Depends(get_session),
    usuario_in: UsuarioCreate,
    # current_user: ModelUsuario = Depends(get_current_active_user) # <--- MANTENER COMENTADO SI ES REGISTRO PÚBLICO
) -> Any:
    """
    Crea un nuevo usuario.
    Si es un endpoint de registro público, no requiere autenticación.
    Si es una función administrativa, requiere autenticación (y posiblemente permisos de superusuario).
    """
    logger.info(f"Intentando crear usuario con username: {usuario_in.username} y email: {usuario_in.email}")

    existing_user_by_email = await crud_usuario.get_by_email(session, email=usuario_in.email)
    if existing_user_by_email:
        logger.warning(f"Intento de crear usuario con email duplicado: {usuario_in.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este email.",
        )
    
    existing_user_by_username = await crud_usuario.get_by_username(session, username=usuario_in.username)
    if existing_user_by_username:
        logger.warning(f"Intento de crear usuario con username duplicado: {usuario_in.username}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este nombre de usuario.",
        )

    try:
        usuario = await crud_usuario.create(session=session, obj_in=usuario_in)
        logger.info(f"Usuario creado exitosamente con ID: {usuario.id}")
        return usuario
    except IntegrityError as e:
        logger.error(f"Error de integridad al crear usuario: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de base de datos: el nombre de usuario o email podría ya existir.",
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear usuario: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno al intentar crear el usuario."
        )

@router.get("/me/", response_model=UsuarioRead)
async def leer_usuario_actual(
    current_user: ModelUsuario = Depends(get_current_active_user),
):
    """
    Obtiene el usuario actual autenticado.
    """
    return current_user

@router.get("/", response_model=List[UsuarioRead], dependencies=[Depends(get_current_active_superuser)])
async def leer_usuarios(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene una lista de usuarios. Solo para superusuarios.
    """
    usuarios = await crud_usuario.get_multi(session, skip=skip, limit=limit)
    return usuarios

@router.get("/{user_id}", response_model=UsuarioRead, dependencies=[Depends(get_current_active_superuser)])
async def leer_usuario_por_id(
    user_id: uuid.UUID, # Se requiere 'import uuid'
    session: AsyncSession = Depends(get_session),
):
    """
    Obtiene un usuario por su ID. Solo para superusuarios.
    """
    usuario = await crud_usuario.get(session, id=user_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario

@router.put("/{user_id}", response_model=UsuarioRead)
async def actualizar_usuario(
    *,
    session: AsyncSession = Depends(get_session),
    user_id: uuid.UUID, # Se requiere 'import uuid'
    usuario_in: UsuarioUpdate,
    current_user: ModelUsuario = Depends(get_current_active_user),
):
    """
    Actualiza un usuario. Un usuario puede actualizarse a sí mismo, o un superusuario puede actualizar a otros.
    """
    db_user = await crud_usuario.get(session, id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Asumiendo que ModelUsuario tiene el atributo 'es_superusuario'
    if db_user.id != current_user.id and not getattr(current_user, 'es_superusuario', False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para actualizar este usuario")

    if usuario_in.email and usuario_in.email != db_user.email:
        existing_user = await crud_usuario.get_by_email(session, email=usuario_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este email ya está en uso por otro usuario.")
            
    # Lógica de validación de username duplicado eliminada ya que UsuarioUpdate no incluye username

    return await crud_usuario.update(session, db_obj=db_user, obj_in=usuario_in)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(
    *,
    session: AsyncSession = Depends(get_session),
    user_id: uuid.UUID, # Se requiere 'import uuid'
    current_user: ModelUsuario = Depends(get_current_active_superuser),
):
    """
    Elimina un usuario. (Lógica de borrado suave o duro según implementación en CRUD)
    """
    db_user = await crud_usuario.get(session, id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    if hasattr(db_user, 'activo') and hasattr(db_user, 'fecha_baja'):
        # Se requiere 'from datetime import datetime'
        update_data = {"activo": False, "fecha_baja": datetime.utcnow()} 
        await crud_usuario.update(session, db_obj=db_user, obj_in=update_data)
    else:
        await crud_usuario.remove(session, id=user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
