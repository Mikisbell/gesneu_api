"""
Enrutador para el módulo de autenticación.

Este módulo define los endpoints de la API relacionados con la autenticación
y gestión de usuarios.
"""
from datetime import timedelta
from typing import Any, Annotated, Optional
from uuid import UUID
import os
import sys
from pathlib import Path

# Asegurarse de que el directorio raíz esté en el path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

# Core imports
from ges_neu_api.core.config import settings
from ges_neu_api.core.database import get_session
from ges_neu_api.core.exceptions import UnauthorizedException

# Local imports
from . import schemas, models
from .dependencies import (
    get_auth_service,
    get_user_service,
    get_role_service,
    get_permission_service,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    has_user_read,
    has_user_write,
    has_user_delete,
    has_role_read,
    has_role_write,
    has_role_delete,
    has_role_manage,
    has_permission_read,
    has_permission_write,
    has_permission_delete,
)
from .service import AuthService, UserService, RoleService, PermissionService

# Crear el router
router = APIRouter(
    tags=["auth"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_session),
) -> schemas.Token:
    """
    Obtiene un token de acceso para el usuario autenticado.
    
    Este endpoint es compatible con el flujo OAuth2 para la autenticación.
    """
    try:
        user = await auth_service.authenticate_user(
            form_data.username, form_data.password
        )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    except UnauthorizedException as e:
        # Captura las excepciones específicas del servicio de autenticación
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Log del error para debugging
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error inesperado en autenticación para usuario '{form_data.username}': {str(e)}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        
        # Devolver error más detallado para debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Error interno del servidor durante la autenticación: {str(e)}",
                "code": "auth_error",
                "details": str(e)
            }
        )

@router.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(
    current_user: schemas.UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> schemas.UserRead:
    """
    Obtiene la información del usuario actualmente autenticado.
    """
    return current_user

@router.post("/users/", response_model=schemas.UserRead)
async def create_user(
    user_in: schemas.UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: schemas.UserRead = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_session),
) -> schemas.UserRead:
    """
    Crea un nuevo usuario.
    
    Solo accesible por superusuarios.
    """
    user = await user_service.get_by_email(email=user_in.email, db=db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )
    
    user = await user_service.create(obj_in=user_in, db=db)
    return user

@router.get("/users/", response_model=list[schemas.UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    _: schemas.UserRead = Depends(has_user_read),
    db: AsyncSession = Depends(get_session),
) -> list[schemas.UserRead]:
    """
    Obtiene una lista de usuarios.
    
    Requiere permiso de lectura de usuarios.
    """
    users = await user_service.get_multi(skip=skip, limit=limit, db=db)
    return users

@router.get("/users/{user_id}", response_model=schemas.UserRead)
async def read_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    _: schemas.UserRead = Depends(has_user_read),
    db: AsyncSession = Depends(get_session),
) -> schemas.UserRead:
    """
    Obtiene un usuario por su ID.
    
    Requiere permiso de lectura de usuarios.
    """
    user = await user_service.get(user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user

@router.put("/users/{user_id}", response_model=schemas.UserRead)
async def update_user(
    user_id: str,
    user_in: schemas.UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: schemas.UserRead = Depends(has_user_write),
    db: AsyncSession = Depends(get_session),
) -> schemas.UserRead:
    """
    Actualiza un usuario existente.
    
    Requiere permiso de escritura de usuarios.
    """
    user = await user_service.get(user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    
    user = await user_service.update(db_obj=user, obj_in=user_in, db=db)
    return user

@router.post("/users/{user_id}/roles/{role_id}", response_model=schemas.UserRead)
async def assign_role_to_user(
    user_id: str,
    role_id: str,
    role_service: RoleService = Depends(get_role_service),
    _: schemas.UserRead = Depends(has_role_manage),
    db: AsyncSession = Depends(get_session),
) -> schemas.UserRead:
    """
    Asigna un rol a un usuario.
    
    Requiere permiso de gestión de roles.
    """
    try:
        user = await role_service.assign_role_to_user(user_id=user_id, role_id=role_id, db=db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.delete("/users/{user_id}/roles/{role_id}", response_model=schemas.UserRead)
async def revoke_role_from_user(
    user_id: str,
    role_id: str,
    role_service: RoleService = Depends(get_role_service),
    _: schemas.UserRead = Depends(has_role_manage),
    db: AsyncSession = Depends(get_session),
) -> schemas.UserRead:
    """
    Revoca un rol de un usuario.
    
    Requiere permiso de gestión de roles.
    """
    try:
        user = await role_service.revoke_role_from_user(user_id=user_id, role_id=role_id, db=db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.delete("/users/{user_id}", response_model=schemas.UserRead)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    _: schemas.UserRead = Depends(has_user_delete),
    db: AsyncSession = Depends(get_session),
) -> schemas.UserRead:
    """
    Elimina un usuario.
    
    Requiere permiso de eliminación de usuarios.
    """
    user = await user_service.get(user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    
    await user_service.remove(id=user_id, db=db)
    return user

# Endpoints para la gestión de roles
@router.post("/roles/", response_model=schemas.RoleInDB, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: schemas.RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    current_user: schemas.UserRead = Depends(has_role_write),
    db: AsyncSession = Depends(get_session),
) -> schemas.RoleInDB:
    """
    Crea un nuevo rol.
    
    Requiere permiso de escritura de roles.
    """
    try:
        db_role = await role_service.create_role(
            role_data=role_in,
            created_by=current_user.id
        )
        return db_role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/roles/", response_model=list[schemas.RoleInDB])
async def read_roles(
    skip: int = 0,
    limit: int = 100,
    nombre: Optional[str] = None,
    role_service: RoleService = Depends(get_role_service),
    _: schemas.UserRead = Depends(has_role_read),
    db: AsyncSession = Depends(get_session),
) -> list[schemas.RoleInDB]:
    """
    Obtiene una lista de roles.
    
    Requiere permiso de lectura de roles.
    """
    roles = await role_service.get_roles(skip=skip, limit=limit, nombre=nombre)
    return roles


@router.get("/roles/{role_id}", response_model=schemas.RoleInDB)
async def read_role(
    role_id: str,
    role_service: RoleService = Depends(get_role_service),
    _: schemas.UserRead = Depends(has_role_read),
    db: AsyncSession = Depends(get_session),
) -> schemas.RoleInDB:
    """
    Obtiene un rol por su ID.
    
    Requiere permiso de lectura de roles.
    """
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de rol no válido",
        )
        
    db_role = await role_service.get_role(role_uuid)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )
    return db_role


@router.put("/roles/{role_id}", response_model=schemas.RoleInDB)
async def update_role(
    role_id: str,
    role_in: schemas.RoleUpdate,
    role_service: RoleService = Depends(get_role_service),
    current_user: schemas.UserRead = Depends(has_role_write),
    db: AsyncSession = Depends(get_session),
) -> schemas.RoleInDB:
    """
    Actualiza un rol existente.
    
    Requiere permiso de escritura de roles.
    """
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de rol no válido",
        )
        
    db_role = await role_service.get_role(role_uuid)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )
        
    # No permitir modificar roles del sistema a menos que sea superusuario
    if db_role.es_rol_sistema and not current_user.es_superusuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para modificar este rol",
        )
    
    try:
        updated_role = await role_service.update_role(
            db_role=db_role,
            role_data=role_in,
            updated_by=current_user.id
        )
        return updated_role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/roles/{role_id}", response_model=schemas.RoleInDB)
async def delete_role(
    role_id: str,
    role_service: RoleService = Depends(get_role_service),
    _: schemas.UserRead = Depends(has_role_delete),
    db: AsyncSession = Depends(get_session),
) -> schemas.RoleInDB:
    """
    Elimina un rol.
    
    Requiere permiso de eliminación de roles.
    No se pueden eliminar roles del sistema ni roles que tengan usuarios asignados.
    """
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de rol no válido",
        )
        
    db_role = await role_service.get_role(role_uuid)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )
    
    try:
        if not await role_service.delete_role(role_uuid):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado",
            )
        return db_role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

# Endpoints para la gestión de permisos
@router.post("/permisos/", 
            response_model=schemas.PermissionInDB, 
            status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_in: schemas.PermissionBase,
    permission_service: PermissionService = Depends(get_permission_service),
    current_user: schemas.UserRead = Depends(has_permission_write),
    db: AsyncSession = Depends(get_session),
) -> schemas.PermissionInDB:
    """
    Crea un nuevo permiso.
    
    Requiere permiso de escritura de permisos.
    """
    try:
        db_permission = await permission_service.create_permission(
            permission_data=permission_in
        )
        return db_permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/permisos/", response_model=list[schemas.PermissionInDB])
async def read_permissions(
    skip: int = 0,
    limit: int = 100,
    nombre_recurso: Optional[str] = None,
    accion: Optional[str] = None,
    permission_service: PermissionService = Depends(get_permission_service),
    _: schemas.UserRead = Depends(has_permission_read),
    db: AsyncSession = Depends(get_session),
) -> list[schemas.PermissionInDB]:
    """
    Obtiene una lista de permisos.
    
    Requiere permiso de lectura de permisos.
    """
    permissions = await permission_service.get_permissions(
        skip=skip, 
        limit=limit,
        nombre_recurso=nombre_recurso,
        accion=accion
    )
    return permissions


@router.get("/permisos/{permission_id}", response_model=schemas.PermissionInDB)
async def read_permission(
    permission_id: str,
    permission_service: PermissionService = Depends(get_permission_service),
    _: schemas.UserRead = Depends(has_permission_read),
    db: AsyncSession = Depends(get_session),
) -> schemas.PermissionInDB:
    """
    Obtiene un permiso por su ID.
    
    Requiere permiso de lectura de permisos.
    """
    try:
        permission_uuid = UUID(permission_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de permiso no válido",
        )
        
    db_permission = await permission_service.get_permission(permission_uuid)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado",
        )
    return db_permission


@router.put("/permisos/{permission_id}", response_model=schemas.PermissionInDB)
async def update_permission(
    permission_id: str,
    permission_in: schemas.PermissionBase,
    permission_service: PermissionService = Depends(get_permission_service),
    _: schemas.UserRead = Depends(has_permission_write),
    db: AsyncSession = Depends(get_session),
) -> schemas.PermissionInDB:
    """
    Actualiza un permiso existente.
    
    Requiere permiso de escritura de permisos.
    No se puede modificar un permiso que esté asignado a roles.
    """
    try:
        permission_uuid = UUID(permission_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de permiso no válido",
        )
        
    db_permission = await permission_service.get_permission(permission_uuid)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado",
        )
    
    try:
        updated_permission = await permission_service.update_permission(
            db_permission=db_permission,
            permission_data=permission_in
        )
        return updated_permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/permisos/{permission_id}", response_model=schemas.PermissionInDB)
async def delete_permission(
    permission_id: str,
    permission_service: PermissionService = Depends(get_permission_service),
    _: schemas.UserRead = Depends(has_permission_delete),
    db: AsyncSession = Depends(get_session),
) -> schemas.PermissionInDB:
    """
    Elimina un permiso.
    
    Requiere permiso de eliminación de permisos.
    No se pueden eliminar permisos asignados a roles.
    """
    try:
        permission_uuid = UUID(permission_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de permiso no válido",
        )
        
    db_permission = await permission_service.get_permission(permission_uuid)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado",
        )
    
    try:
        if not await permission_service.delete_permission(permission_uuid):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permiso no encontrado",
            )
        return db_permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
