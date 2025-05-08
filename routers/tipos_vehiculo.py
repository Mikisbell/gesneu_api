# routers/tipos_vehiculo.py (Refactorizado con CRUD)
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
from models.tipo_vehiculo import TipoVehiculo # El modelo
from models.usuario import Usuario
# Importar los schemas que creamos
from schemas.tipo_vehiculo import TipoVehiculoCreate, TipoVehiculoRead, TipoVehiculoUpdate
# Importar el objeto CRUD
from crud.crud_tipo_vehiculo import tipo_vehiculo as crud_tipo_vehiculo

# Crear el router específico
router = APIRouter(
    tags=["Tipos de Vehículo"], # Mantener tags
    dependencies=[Depends(get_current_active_user)] # Usar la dependencia centralizada
)

logger = logging.getLogger(__name__)

@router.post(
    "/", # Ruta relativa al prefijo: /tipos-vehiculo/
    response_model=TipoVehiculoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo tipo de vehículo"
)
async def crear_tipo_vehiculo(
    tipo_vehiculo_in: TipoVehiculoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crea un nuevo registro de tipo de vehículo."""
    # Verificación de duplicado por nombre usando el CRUD
    existing_tipo_vehiculo_nombre = await crud_tipo_vehiculo.get_by_name(session, name=tipo_vehiculo_in.nombre)
    if existing_tipo_vehiculo_nombre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un tipo de vehículo con el nombre '{tipo_vehiculo_in.nombre}'"
        )

    # Crear instancia y asignar auditoría usando el CRUD
    # Añadir el usuario creador antes de pasar al CRUD si el CRUD base no lo maneja
    tipo_vehiculo_data = tipo_vehiculo_in.model_dump()
    tipo_vehiculo_data['creado_por'] = current_user.id

    # El CRUD base maneja la adición, commit y refresh
    try:
        # Pasar el diccionario de datos, no el schema directamente, para incluir 'creado_por'
        db_tipo_vehiculo = await crud_tipo_vehiculo.create(session, obj_in=tipo_vehiculo_in) # Pasar el schema directamente
        logger.info(f"Tipo de Vehículo '{db_tipo_vehiculo.nombre}' creado por {current_user.username}")
        return db_tipo_vehiculo
    except IntegrityError as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.warning(f"Error de integridad al crear tipo vehículo (posible duplicado BD): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al guardar. El nombre '{tipo_vehiculo_in.nombre}' ya podría existir (insensible a mayúsculas/acentos) o hubo otro problema."
        )
    except Exception as e:
         # El CRUD base ya hizo rollback si falló el commit
         logger.error(f"Error inesperado al crear tipo vehículo: {str(e)}", exc_info=True)
         raise HTTPException(
              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Error interno al crear el tipo de vehículo."
          )

@router.get(
    "/", # Ruta relativa: /tipos-vehiculo/
    response_model=List[TipoVehiculoRead],
    summary="Listar tipos de vehículo"
)
async def leer_tipos_vehiculo(
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo")
):
    """Obtiene una lista paginada de tipos de vehículo."""
    if activo is True:
        # Usar el método específico para activos
        tipos_vehiculo = await crud_tipo_vehiculo.get_multi_active(session, skip=skip, limit=limit)
    elif activo is False:
        # Si se pide inactivos, necesitamos un método específico o filtrar aquí
        # Por ahora, obtendremos todos y filtraremos (menos eficiente para grandes datasets)
        # O mejor, añadimos un método get_multi_inactive al CRUD si es necesario frecuentemente
        # Para simplificar, usaremos get_multi y filtraremos si activo is False
        all_tipos_vehiculo = await crud_tipo_vehiculo.get_multi(session, skip=skip, limit=limit)
        tipos_vehiculo = [tv for tv in all_tipos_vehiculo if not tv.activo]
    else: # activo is None (obtener todos)
        tipos_vehiculo = await crud_tipo_vehiculo.get_multi(session, skip=skip, limit=limit)

    # Nota: La ordenación por nombre no está en el CRUD base get_multi.
    # Si la ordenación es crucial, se debe añadir al método CRUD o manejar aquí.
    # Por ahora, devolvemos como vienen del CRUD base/filtrado.
    return tipos_vehiculo

@router.get(
    "/{tipo_vehiculo_id}", # Ruta relativa: /tipos-vehiculo/{id}
    response_model=TipoVehiculoRead,
    summary="Obtener tipo de vehículo por ID"
)
async def leer_tipo_vehiculo_por_id(
    tipo_vehiculo_id: uuid.UUID = Path(..., description="ID único del tipo de vehículo"),
    session: AsyncSession = Depends(get_session)
    # current_user: Usuario = Depends(get_current_active_user) # Ya protegido a nivel router
):
    """Obtiene los detalles de un tipo de vehículo específico."""
    # Usar el método get del CRUD
    db_tipo_vehiculo = await crud_tipo_vehiculo.get(session, id=tipo_vehiculo_id)
    if not db_tipo_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de vehículo con ID {tipo_vehiculo_id} no encontrado."
        )
    return db_tipo_vehiculo

@router.put(
    "/{tipo_vehiculo_id}", # Ruta relativa: /tipos-vehiculo/{id}
    response_model=TipoVehiculoRead,
    summary="Actualizar un tipo de vehículo"
)
async def actualizar_tipo_vehiculo(
    tipo_vehiculo_id: uuid.UUID,
    tipo_vehiculo_update: TipoVehiculoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Actualiza los datos de un tipo de vehículo existente."""
    # Obtener el tipo de vehículo usando el CRUD
    db_tipo_vehiculo = await crud_tipo_vehiculo.get(session, id=tipo_vehiculo_id)
    if not db_tipo_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de vehículo con ID {tipo_vehiculo_id} no encontrado para actualizar."
        )

    update_data = tipo_vehiculo_update.model_dump(exclude_unset=True)

    # Verificación de duplicado por nombre (si se está actualizando el nombre)
    if "nombre" in update_data and update_data["nombre"] != db_tipo_vehiculo.nombre:
        existing_tipo_vehiculo_nombre = await crud_tipo_vehiculo.get_by_name(session, name=update_data["nombre"])
        if existing_tipo_vehiculo_nombre and existing_tipo_vehiculo_nombre.id != tipo_vehiculo_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro tipo de vehículo con el nombre '{update_data['nombre']}'"
            )

    # Añadir usuario actualizador antes de pasar al CRUD si el CRUD base no lo maneja
    update_data['actualizado_en'] = datetime.now(timezone.utc)
    update_data['actualizado_por'] = current_user.id

    # Actualizar el tipo de vehículo usando el CRUD
    try:
        db_tipo_vehiculo = await crud_tipo_vehiculo.update(session, db_obj=db_tipo_vehiculo, obj_in=update_data) # Pasar el diccionario de actualización
        logger.info(f"Tipo Vehículo {tipo_vehiculo_id} actualizado por {current_user.username}")
        return db_tipo_vehiculo
    except IntegrityError as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.warning(f"Error de integridad al actualizar tipo vehículo {tipo_vehiculo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al guardar. El nombre '{update_data.get('nombre', db_tipo_vehiculo.nombre)}' ya podría existir (insensible a mayúsculas/acentos) o hubo otro problema."
        )
    except Exception as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error inesperado al actualizar tipo vehículo {tipo_vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar tipo de vehículo."
        )

@router.delete(
    "/{tipo_vehiculo_id}", # Ruta relativa: /tipos-vehiculo/{id}
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar un tipo de vehículo (Eliminación lógica)"
)
async def desactivar_tipo_vehiculo(
    tipo_vehiculo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Marca un tipo de vehículo como inactivo."""
    # Obtener el tipo de vehículo usando el CRUD
    db_tipo_vehiculo = await crud_tipo_vehiculo.get(session, id=tipo_vehiculo_id)
    if not db_tipo_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de vehículo con ID {tipo_vehiculo_id} no encontrado para desactivar."
        )

    if not db_tipo_vehiculo.activo:
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
        await crud_tipo_vehiculo.update(session, db_obj=db_tipo_vehiculo, obj_in=update_data)
        logger.info(f"Tipo Vehículo {tipo_vehiculo_id} desactivado por {current_user.username}")
        # No se devuelve contenido en 204
    except Exception as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error al desactivar tipo vehículo {tipo_vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # O 500
            detail=f"No se pudo desactivar el tipo de vehículo. Puede estar en uso por vehículos existentes. Detalle DB: {str(e)}"
        )
