# routers/vehiculo.py
import uuid
import logging
from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
# --- Asegurar importación de AsyncSession desde SQLModel ---
from sqlmodel.ext.asyncio.session import AsyncSession # <--- Desde SQLModel
from sqlalchemy.exc import IntegrityError

from core.dependencies import get_session # Usar la dependencia centralizada
from core.dependencies import get_current_active_user # Usar la dependencia centralizada
from models.vehiculo import Vehiculo
from schemas.vehiculo import VehiculoCreate, VehiculoRead, VehiculoUpdate
from models.usuario import Usuario # Asumiendo que Usuario está definido
# Importar el objeto CRUD
from crud.crud_vehiculo import vehiculo as crud_vehiculo

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=VehiculoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo vehículo"
)
async def crear_vehiculo(
    vehiculo_in: VehiculoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Crea un nuevo registro de vehículo"""
    # Verificar duplicados usando el CRUD
    existing_vehiculo_eco = await crud_vehiculo.get_by_numero_economico(session, numero_economico=vehiculo_in.numero_economico)
    if existing_vehiculo_eco:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe vehículo con número económico '{vehiculo_in.numero_economico}'"
        )

    if vehiculo_in.placa:
        existing_vehiculo_placa = await crud_vehiculo.get_by_placa(session, placa=vehiculo_in.placa)
        if existing_vehiculo_placa:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe vehículo con placa '{vehiculo_in.placa}'"
            )

    # Preparar datos y crear usando el CRUD
    # Añadir el usuario creador antes de pasar al CRUD si el CRUD base no lo maneja
    vehiculo_data = vehiculo_in.model_dump(exclude_unset=True)
    vehiculo_data["creado_por"] = current_user.id

    # Intentar guardar en BD usando el CRUD
    try:
        # Pasar el schema de entrada directamente al método create del CRUD
        db_vehiculo = await crud_vehiculo.create(session, obj_in=vehiculo_in)
        logger.info(f"Vehículo {db_vehiculo.numero_economico} creado por {current_user.username}")
        return db_vehiculo
    except IntegrityError as e: # Captura específica para errores de BD al guardar
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error de integridad (inesperado aquí?) al crear vehículo: {str(e)}", exc_info=True)
        # Si llegamos aquí, es un error de BD no detectado antes (ej. otra constraint)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al guardar el vehículo."
        )
    except Exception as e:
         # El CRUD base ya hizo rollback si falló el commit
         logger.error(f"Error inesperado al crear vehículo: {str(e)}", exc_info=True)
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail="Error interno del servidor al crear el vehículo."
         )

@router.get(
    "/",
    response_model=List[VehiculoRead],
    summary="Listar vehículos"
)
async def leer_vehiculos(
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(get_current_active_user), # Usar la dependencia centralizada
    skip: int = 0,
    limit: int = Query(default=100, le=200),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo") # Default None para ver todos
):
    """Obtiene una lista de vehículos filtrados por estado"""
    # Usar el método get_multi o get_multi_active del CRUD
    if activo is True:
        vehiculos = await crud_vehiculo.get_multi_active(session, skip=skip, limit=limit)
    elif activo is False:
        # Si se pide inactivos, necesitamos un método específico o filtrar aquí
        # Para simplificar, usaremos get_multi y filtraremos si activo is False
        all_vehiculos = await crud_vehiculo.get_multi(session, skip=skip, limit=limit)
        vehiculos = [v for v in all_vehiculos if not v.activo]
    else: # activo is None (obtener todos)
        vehiculos = await crud_vehiculo.get_multi(session, skip=skip, limit=limit)

    # Nota: La ordenación por numero_economico no está en el CRUD base get_multi.
    # Si la ordenación es crucial, se debe añadir al método CRUD o manejar aquí.
    # Por ahora, devolvemos como vienen del CRUD base/filtrado.
    return vehiculos

@router.get(
    "/{vehiculo_id}",
    response_model=VehiculoRead,
    summary="Obtener vehículo por ID"
)
async def leer_vehiculo_por_id(
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(get_current_active_user), # Usar la dependencia centralizada
    vehiculo_id: uuid.UUID = Path(..., description="ID único del vehículo a obtener") # '...' indica requerido
):
    """Obtiene los detalles de un vehículo específico por su ID."""
    """Obtiene los detalles de un vehículo específico"""
    # Usar el método get del CRUD
    vehiculo = await crud_vehiculo.get(session, id=vehiculo_id)
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado."
        )
    return vehiculo

@router.put(
    "/{vehiculo_id}",
    response_model=VehiculoRead,
    summary="Actualizar vehículo"
)
async def actualizar_vehiculo(
    vehiculo_update: VehiculoUpdate,
    vehiculo_id: uuid.UUID = Path(..., description="ID del vehículo a actualizar"),
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Actualiza los datos de un vehículo existente."""
    """Actualiza los datos de un vehículo existente"""
    # Obtener el vehículo usando el CRUD
    db_vehiculo = await crud_vehiculo.get(session, id=vehiculo_id)
    if not db_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado para actualizar."
        )

    update_data = vehiculo_update.model_dump(exclude_unset=True)

    # Verificar duplicados antes de intentar guardar usando el CRUD
    if "numero_economico" in update_data and update_data["numero_economico"] != db_vehiculo.numero_economico:
        existing_vehiculo_eco = await crud_vehiculo.get_by_numero_economico(session, numero_economico=update_data["numero_economico"])
        if existing_vehiculo_eco and existing_vehiculo_eco.id != vehiculo_id: # Asegurarse que no es el mismo vehículo
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Número económico '{update_data['numero_economico']}' ya existe.")

    if "placa" in update_data and update_data["placa"] != db_vehiculo.placa:
        existing_vehiculo_placa = await crud_vehiculo.get_by_placa(session, placa=update_data["placa"])
        if existing_vehiculo_placa and existing_vehiculo_placa.id != vehiculo_id: # Asegurarse que no es el mismo vehículo
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Placa '{update_data['placa']}' ya existe.")

    # Actualizar campos usando el CRUD
    # Añadir campos de auditoría antes de pasar al CRUD si el CRUD base no lo maneja
    update_data['actualizado_en'] = datetime.now(timezone.utc)
    update_data['actualizado_por'] = current_user.id

    # Intentar guardar usando el CRUD
    try:
        # Pasar el objeto de BD y el diccionario de actualización al método update del CRUD
        db_vehiculo = await crud_vehiculo.update(session, db_obj=db_vehiculo, obj_in=update_data)
        logger.info(f"Vehículo {vehiculo_id} actualizado por {current_user.username}")
        return db_vehiculo
    except IntegrityError as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error de integridad al actualizar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al actualizar."
        )
    except Exception as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error inesperado al actualizar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar vehículo."
        )

@router.delete(
    "/{vehiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Inactivar vehículo (Eliminación lógica)"
)
async def eliminar_vehiculo(
    vehiculo_id: uuid.UUID = Path(..., description="ID del vehículo a inactivar"),
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Realiza una eliminación lógica del vehículo"""
    # --- Misma lógica de excepción que en PUT/GET ID ---
    # Obtener el vehículo usando el CRUD
    vehiculo = await crud_vehiculo.get(session, id=vehiculo_id)
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado para eliminar."
        )
    if not vehiculo.activo:
        return # Idempotente

    # Marcar como inactivo usando el método update del CRUD
    # Pasamos un diccionario con los campos a actualizar
    update_data = {
        "activo": False,
        "fecha_baja": date.today(),
        "actualizado_en": datetime.now(timezone.utc),
        "actualizado_por": current_user.id
    }
    try:
        await crud_vehiculo.update(session, db_obj=vehiculo, obj_in=update_data)
        logger.info(f"Vehículo {vehiculo_id} inactivado por {current_user.username}")
        # No se devuelve contenido en 204
    except Exception as e: # Captura errores inesperados al guardar
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error al inactivar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud de inactivación."
        )