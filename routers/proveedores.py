# routers/proveedores.py (Refactorizado con CRUD)
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

# Dependencias y modelos/schemas necesarios
from core.dependencies import get_session # Usar la dependencia centralizada
from core.dependencies import get_current_active_user # Usar la dependencia centralizada
from models.proveedor import Proveedor
from models.usuario import Usuario # Para obtener el current_user
from schemas.proveedor import ProveedorCreate, ProveedorRead, ProveedorUpdate
# Importar el objeto CRUD
from crud.crud_proveedor import proveedor as crud_proveedor

# Crear el router específico para proveedores
router = APIRouter(
    tags=["Proveedores"], # Etiqueta para la documentación de Swagger UI
    dependencies=[Depends(get_current_active_user)] # Proteger todos los endpoints
)

logger = logging.getLogger(__name__)

@router.post(
    "/", # Ruta relativa: POST /proveedores/
    response_model=ProveedorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proveedor"
)
async def crear_proveedor(
    proveedor_in: ProveedorCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Crea un nuevo registro de proveedor en la base de datos."""
    # Verificar duplicado por nombre usando el CRUD
    existing_proveedor_nombre = await crud_proveedor.get_by_name(session, name=proveedor_in.nombre)
    if existing_proveedor_nombre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un proveedor con el nombre '{proveedor_in.nombre}'"
        )

    # Preparar datos y crear instancia del modelo usando el CRUD
    # Añadir el usuario creador antes de pasar al CRUD si el CRUD base no lo maneja
    proveedor_data = proveedor_in.model_dump()
    proveedor_data['creado_por'] = current_user.id
    # El CRUD base maneja la adición, commit y refresh
    try:
        db_proveedor = await crud_proveedor.create(session, obj_in=proveedor_in) # Pasar el schema directamente
        logger.info(f"Proveedor '{db_proveedor.nombre}' creado por {current_user.username}")
        return db_proveedor
    except IntegrityError as e: # Captura errores de BD al guardar
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error de integridad al crear proveedor: {str(e)}", exc_info=True)
        # Podría ser un duplicado no detectado antes u otra constraint
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al guardar el proveedor."
        )
    except Exception as e:
         # El CRUD base ya hizo rollback si falló el commit
         logger.error(f"Error inesperado al crear proveedor: {str(e)}", exc_info=True)
         raise HTTPException(
              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Error interno al crear el proveedor."
          )


@router.get(
    "/", # Ruta relativa: GET /proveedores/
    response_model=List[ProveedorRead],
    summary="Listar proveedores"
)
async def leer_proveedores(
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo")
    # current_user: Usuario = Depends(get_current_active_user) # Ya protegido a nivel router
):
    """Obtiene una lista paginada de proveedores, opcionalmente filtrada por estado."""
    if activo is True:
        # Usar el método específico para activos
        proveedores = await crud_proveedor.get_multi_active(session, skip=skip, limit=limit)
    elif activo is False:
        # Si se pide inactivos, necesitamos un método específico o filtrar aquí
        # Por ahora, obtendremos todos y filtraremos (menos eficiente para grandes datasets)
        # O mejor, añadimos un método get_multi_inactive al CRUD si es necesario frecuentemente
        # Para simplificar, usaremos get_multi y filtraremos si activo is False
        all_proveedores = await crud_proveedor.get_multi(session, skip=skip, limit=limit)
        proveedores = [p for p in all_proveedores if not p.activo]
    else: # activo is None (obtener todos)
        proveedores = await crud_proveedor.get_multi(session, skip=skip, limit=limit)

    # Nota: La ordenación por nombre no está en el CRUD base get_multi.
    # Si la ordenación es crucial, se debe añadir al método CRUD o manejar aquí.
    # Por ahora, devolvemos como vienen del CRUD base/filtrado.
    return proveedores


@router.get(
    "/{proveedor_id}", # Ruta relativa: GET /proveedores/{proveedor_id}
    response_model=ProveedorRead,
    summary="Obtener proveedor por ID"
)
async def leer_proveedor_por_id(
    proveedor_id: uuid.UUID = Path(..., description="ID único del proveedor a obtener"),
    session: AsyncSession = Depends(get_session)
    # current_user: Usuario = Depends(get_current_active_user) # Ya protegido
):
    """Obtiene los detalles de un proveedor específico por su ID."""
    # Usar el método get del CRUD
    db_proveedor = await crud_proveedor.get(session, id=proveedor_id)
    if not db_proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {proveedor_id} no encontrado."
        )
    return db_proveedor


@router.put(
    "/{proveedor_id}", # Ruta relativa: PUT /proveedores/{proveedor_id}
    response_model=ProveedorRead,
    summary="Actualizar un proveedor"
)
async def actualizar_proveedor(
    proveedor_id: uuid.UUID,
    proveedor_update: ProveedorUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Actualiza los datos de un proveedor existente."""
    # Obtener el proveedor usando el CRUD
    db_proveedor = await crud_proveedor.get(session, id=proveedor_id)
    if not db_proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {proveedor_id} no encontrado para actualizar."
        )

    update_data = proveedor_update.model_dump(exclude_unset=True) # Solo campos enviados

    # Verificar duplicado por nombre si se está cambiando
    if "nombre" in update_data and update_data["nombre"] != db_proveedor.nombre:
        existing_proveedor_nombre = await crud_proveedor.get_by_name(session, name=update_data["nombre"])
        if existing_proveedor_nombre and existing_proveedor_nombre.id != proveedor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro proveedor con el nombre '{update_data['nombre']}'"
            )

    # Añadir usuario actualizador antes de pasar al CRUD si el CRUD base no lo maneja
    update_data['actualizado_en'] = datetime.now(timezone.utc)
    update_data['actualizado_por'] = current_user.id

    # Actualizar el proveedor usando el CRUD
    try:
        db_proveedor = await crud_proveedor.update(session, db_obj=db_proveedor, obj_in=update_data) # Pasar el diccionario de actualización
        logger.info(f"Proveedor {proveedor_id} actualizado por {current_user.username}")
        return db_proveedor
    except IntegrityError as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.warning(f"Error de integridad al actualizar proveedor {proveedor_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al actualizar proveedor."
        )
    except Exception as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error inesperado al actualizar proveedor {proveedor_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar proveedor."
        )


@router.delete(
    "/{proveedor_id}", # Ruta relativa: DELETE /proveedores/{proveedor_id}
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar un proveedor (Eliminación lógica)"
)
async def desactivar_proveedor(
    proveedor_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Marca un proveedor como inactivo (eliminación lógica)."""
    # Obtener el proveedor usando el CRUD
    db_proveedor = await crud_proveedor.get(session, id=proveedor_id)
    if not db_proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {proveedor_id} no encontrado para desactivar."
        )

    if not db_proveedor.activo:
        # Ya está inactivo, no hacer nada (idempotente)
        return # Devuelve 204 implícitamente

    # Actualizar el estado activo a False usando el método update del CRUD
    # Pasamos un diccionario con solo el campo a actualizar
    update_data = {
        "activo": False,
        "actualizado_en": datetime.now(timezone.utc),
        "actualizado_por": current_user.id
    }
    try:
        await crud_proveedor.update(session, db_obj=db_proveedor, obj_in=update_data)
        logger.info(f"Proveedor {proveedor_id} desactivado por {current_user.username}")
        # No se devuelve contenido en 204
    except Exception as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error al desactivar proveedor {proveedor_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al desactivar proveedor."
        )
