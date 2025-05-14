# gesneu_api2/routers/usuarios.py
import uuid # <--- IMPORTACIÓN AÑADIDA
from datetime import datetime, timezone # <--- IMPORTACIÓN AÑADIDA Y ACTUALIZADA
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import traceback

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
    try:
        # Usar un enfoque directo con SQLAlchemy raw
        from sqlalchemy import select
        from models.usuario import Usuario
        import logging
        
        logger = logging.getLogger("GesNeuAPI")
        
        # Construir la consulta seleccionando el modelo completo
        statement = select(Usuario).offset(skip).limit(limit)
        logger.info(f"Ejecutando consulta: {statement}")
        
        result = await session.exec(statement)
        
        # CORRECCIÓN: Usar scalars().all() para obtener directamente instancias del modelo Usuario
        usuario_models = result.scalars().all()  # Esto devuelve List[Usuario]
        logger.info(f"Número de usuarios encontrados: {len(usuario_models)}")
        
        # Convertir a lista de diccionarios para la respuesta
        usuarios_response = []
        
        # Imprimir el tipo de objeto para depuración
        if usuario_models:
            logger.info(f"Tipo de objeto usuario: {type(usuario_models[0])}")
        
        for i, usuario_model in enumerate(usuario_models):
            try:
                logger.info(f"Procesando usuario {i+1}: {usuario_model.username}")
                
                # 'usuario_model' es ahora una instancia de tu modelo 'Usuario'
                usuario_dict = {
                    "id": str(usuario_model.id),  # Correcto: accede al 'id' del modelo
                    "username": usuario_model.username,
                    "email": usuario_model.email,
                    "activo": usuario_model.activo,
                    "creado_en": usuario_model.creado_en,
                }
                
                # Añadir atributos opcionales solo si existen
                if hasattr(usuario_model, 'nombre_completo'):
                    usuario_dict["nombre_completo"] = usuario_model.nombre_completo
                else:
                    usuario_dict["nombre_completo"] = None
                    
                # Determinar el rol basado en los permisos del usuario
                if hasattr(usuario_model, 'es_superusuario') and usuario_model.es_superusuario:
                    usuario_dict["rol"] = "ADMIN"
                else:
                    usuario_dict["rol"] = "OPERADOR"  # Valor predeterminado para usuarios no superusuarios
                    
                if hasattr(usuario_model, 'actualizado_en'):
                    usuario_dict["actualizado_en"] = usuario_model.actualizado_en
                else:
                    usuario_dict["actualizado_en"] = None
                    
                usuarios_response.append(usuario_dict)
                logger.info(f"Usuario añadido a la respuesta: {usuario_dict['username']}")
            except Exception as e:
                logger.error(f"Error procesando usuario {i+1}: {str(e)}")
                # Continuar con el siguiente usuario
        
        logger.info(f"Total de usuarios en la respuesta: {len(usuarios_response)}")
        return usuarios_response
    
    except Exception as e:
        error_msg = f"Error en leer_usuarios: {e}"
        stack_trace = traceback.format_exc()
        logger.error(f"{error_msg}\n{stack_trace}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

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
        # Se requiere 'from datetime import datetime, timezone'
        update_data = {"activo": False, "fecha_baja": datetime.now(timezone.utc)} 
        await crud_usuario.update(session, db_obj=db_user, obj_in=update_data)
    else:
        await crud_usuario.remove(session, id=user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
