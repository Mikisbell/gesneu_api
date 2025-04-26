# routers/usuarios.py
import logging
import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from database import get_session
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate
from core.security import get_password_hash
import auth
# --- APIRouter SIN el prefijo ---
router = APIRouter(
    tags=["Usuarios"]    # El prefijo se define en main.py
)
logger = logging.getLogger(__name__)

@router.post("/", response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario"
)
async def crear_usuario(
    usuario_in: UsuarioCreate,
    session: AsyncSession = Depends(get_session)
    # current_active_user: Usuario = Depends(auth.get_current_active_user) # Para proteger
):
    """
    Crea un nuevo usuario en el sistema con su contraseña hasheada.
    """
    # 1. Verificar si el username ya existe
    stmt_username = select(Usuario).where(Usuario.username == usuario_in.username)
    result_username = await session.exec(stmt_username)
    if result_username.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El nombre de usuario '{usuario_in.username}' ya está registrado."
        )

    # 2. Verificar si el email ya existe (si se proporcionó y es único)
    if usuario_in.email:
        stmt_email = select(Usuario).where(Usuario.email == usuario_in.email)
        result_email = await session.exec(stmt_email)
        if result_email.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El email '{usuario_in.email}' ya está registrado."
            )

    # 3. Hashear la contraseña antes de guardar
    hashed_password = get_password_hash(usuario_in.password)

    # 4. Crear el diccionario de datos para el modelo de BD
    usuario_data = usuario_in.model_dump(exclude={"password"})
    usuario_data["password_hash"] = hashed_password
    # usuario_data["creado_por"] = current_active_user.id # Si estuviera protegido

    # 5. Crear la instancia del modelo Usuario
    db_usuario = Usuario.model_validate(usuario_data)

    # 6. Añadir a la sesión y guardar en la BD
    session.add(db_usuario)
    try:
        await session.commit()
        await session.refresh(db_usuario)
        logger.info(f"Usuario '{db_usuario.username}' creado exitosamente.")
        return db_usuario
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad al crear usuario: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al crear usuario (username o email duplicado)."
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado al crear usuario: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear el usuario."
        )

# --- Endpoint: Obtener Usuario Actual ---
@router.get(
    "/me/",
    response_model=UsuarioRead,
    summary="Obtener datos del usuario actual"
)
async def read_users_me(
    current_user: Usuario = Depends(auth.get_current_active_user) # ASUMIENDO QUE ESTA DEPENDENCIA EXISTE EN auth.py
):
    """
    Devuelve los detalles del usuario que realiza la petición (autenticado).
    """
    return current_user

# --- Endpoint: Listar Usuarios ---
@router.get(
    "/",
    response_model=List[UsuarioRead],
    summary="Listar usuarios registrados"
)
async def read_users(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = Query(default=100, le=200),
    current_user: Usuario = Depends(auth.get_current_active_user) # ASUMIENDO QUE ESTA DEPENDENCIA EXISTE EN auth.py
    # if current_user.rol != "ADMIN": # Lógica de roles opcional
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos")
):
    """
    Obtiene una lista paginada de usuarios registrados en el sistema.
    (Actualmente accesible por cualquier usuario activo).
    """
    statement = select(Usuario).offset(skip).limit(limit).order_by(Usuario.username)
    results = await session.exec(statement)
    users = results.all()
    return users

# --- La ruta GET /test-ruta/ ha sido eliminada ---
# --- NUEVO ENDPOINT: Obtener Usuario por ID ---
@router.get(
    "/{user_id}",
    response_model=UsuarioRead,
    summary="Obtener un usuario por su ID"
)
async def read_user_by_id(
    user_id: uuid.UUID, # Parámetro de ruta para el ID
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user) # Proteger endpoint
    # Podrías añadir lógica de permisos aquí (ej. solo admins ven otros usuarios)
):
    """Obtiene los detalles de un usuario específico por su ID."""
    user = await session.get(Usuario, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado."
        )
    # Verificar permisos si es necesario
    # if user.id != current_user.id and current_user.rol != "ADMIN":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")
    return user

# --- NUEVO ENDPOINT: Actualizar Usuario ---
@router.put(
    "/{user_id}",
    response_model=UsuarioRead,
    summary="Actualizar un usuario existente"
)
async def update_user(
    user_id: uuid.UUID,
    usuario_update: UsuarioUpdate, # Datos para actualizar
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user) # Proteger endpoint
):
    """Actualiza los datos de un usuario existente (excepto username y password)."""
    db_user = await session.get(Usuario, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado para actualizar."
        )

    # Verificar permisos (ej: solo admin o el propio usuario pueden actualizar)
    # if db_user.id != current_user.id and current_user.rol != "ADMIN":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permitido")

    update_data = usuario_update.model_dump(exclude_unset=True) # Obtener solo campos enviados

    # Verificar si se intenta cambiar email a uno existente
    if "email" in update_data and update_data["email"] != db_user.email:
        stmt_email = select(Usuario).where(Usuario.email == update_data["email"])
        result_email = await session.exec(stmt_email)
        if result_email.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El email '{update_data['email']}' ya está en uso."
            )

    # Actualizar campos del modelo
    for key, value in update_data.items():
        setattr(db_user, key, value)

    # Actualizar campos de auditoría
    db_user.actualizado_en = datetime.now(timezone.utc) # Necesitas importar datetime, timezone
    db_user.actualizado_por = current_user.id

    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user)
        logger.info(f"Usuario '{db_user.username}' (ID: {user_id}) actualizado por '{current_user.username}'.")
        return db_user
    except IntegrityError as e: # Por si acaso hay otra constraint
        await session.rollback()
        logger.error(f"Error de integridad al actualizar usuario {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al actualizar usuario."
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado al actualizar usuario {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar usuario."
        )


# --- NUEVO ENDPOINT: Eliminar Usuario (Lógico) ---
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT, # No devuelve contenido
    summary="Eliminar lógicamente un usuario"
)
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user) # Proteger endpoint
):
    """
    Marca un usuario como inactivo (eliminación lógica).
    Requiere permisos adecuados (ej. solo un ADMIN).
    """
    # --- Lógica de Permisos ---
    # ¡Importante! Decide quién puede eliminar usuarios.
    # Generalmente, no quieres que un usuario normal elimine a otros.
    # if current_user.rol != "ADMIN":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar usuarios.")
    # if current_user.id == user_id:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes eliminarte a ti mismo.")
    # -------------------------

    db_user = await session.get(Usuario, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado para eliminar."
        )

    if not db_user.activo:
        # Si ya está inactivo, la operación es idempotente. Simplemente retorna.
        return # O podrías devolver Response(status_code=status.HTTP_204_NO_CONTENT)

    # Marcar como inactivo (eliminación lógica)
    db_user.activo = False
    db_user.actualizado_en = datetime.now(timezone.utc) # Necesitas importar datetime, timezone
    db_user.actualizado_por = current_user.id

    session.add(db_user)
    try:
        await session.commit()
        logger.info(f"Usuario '{db_user.username}' (ID: {user_id}) marcado como inactivo por '{current_user.username}'.")
        # No se devuelve contenido en un 204
        # return Response(status_code=status.HTTP_204_NO_CONTENT) # Alternativa explícita
    except Exception as e: # Captura errores genéricos al guardar
        await session.rollback()
        logger.error(f"Error al marcar como inactivo al usuario {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al eliminar usuario."
        )


# --- Fin de los nuevos endpoints ---
