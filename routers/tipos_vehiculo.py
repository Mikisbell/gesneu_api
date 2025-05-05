# routers/tipos_vehiculo.py (Corregido - Sin Prefijo Interno)
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func # Para usar func.lower si refinas el check

# Dependencias y modelos/schemas necesarios
import auth
from database import get_session
from models.tipo_vehiculo import TipoVehiculo # El modelo
from models.usuario import Usuario
# Importar los schemas que creamos
from schemas.tipo_vehiculo import TipoVehiculoCreate, TipoVehiculoRead, TipoVehiculoUpdate

# Crear el router específico
# --- CORRECCIÓN: Eliminar el argumento prefix ---
router = APIRouter(
    tags=["Tipos de Vehículo"], # Mantener tags
    dependencies=[Depends(auth.get_current_active_user)] # Mantener dependencias globales
)
# --- FIN CORRECCIÓN ---

logger = logging.getLogger(__name__)

# El resto del código (endpoints @router.post, @router.get, etc.) permanece igual
# ... (pega aquí el resto de tu código original para este archivo) ...

@router.post(
    "/", # Ruta relativa al prefijo: /tipos-vehiculo/
    response_model=TipoVehiculoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo tipo de vehículo"
)
async def crear_tipo_vehiculo(
    tipo_vehiculo_in: TipoVehiculoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Crea un nuevo registro de tipo de vehículo."""
    # Verificación simple de duplicado
    stmt_nombre = select(TipoVehiculo).where(TipoVehiculo.nombre == tipo_vehiculo_in.nombre)
    result_nombre = await session.exec(stmt_nombre)
    if result_nombre.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un tipo de vehículo con el nombre '{tipo_vehiculo_in.nombre}'"
        )

    # Crear instancia y asignar auditoría
    tipo_vehiculo_data = tipo_vehiculo_in.model_dump()
    db_tipo_vehiculo = TipoVehiculo.model_validate(tipo_vehiculo_data)
    db_tipo_vehiculo.creado_por = current_user.id

    # Guardar en BD
    session.add(db_tipo_vehiculo)
    try:
        await session.commit()
        await session.refresh(db_tipo_vehiculo)
        logger.info(f"Tipo de Vehículo '{db_tipo_vehiculo.nombre}' creado por {current_user.username}")
        return db_tipo_vehiculo
    except IntegrityError as e:
        await session.rollback()
        logger.warning(f"Error de integridad al crear tipo vehículo (posible duplicado BD): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al guardar. El nombre '{tipo_vehiculo_in.nombre}' ya podría existir (insensible a mayúsculas/acentos) o hubo otro problema."
        )
    except Exception as e:
         await session.rollback()
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
    statement = select(TipoVehiculo)
    if activo is not None:
        statement = statement.where(TipoVehiculo.activo == activo)
    statement = statement.order_by(TipoVehiculo.nombre).offset(skip).limit(limit)
    results = await session.exec(statement)
    tipos_vehiculo = results.all()
    return tipos_vehiculo

@router.get(
    "/{tipo_vehiculo_id}", # Ruta relativa: /tipos-vehiculo/{id}
    response_model=TipoVehiculoRead,
    summary="Obtener tipo de vehículo por ID"
)
async def leer_tipo_vehiculo_por_id(
    tipo_vehiculo_id: uuid.UUID = Path(..., description="ID único del tipo de vehículo"),
    session: AsyncSession = Depends(get_session)
):
    """Obtiene los detalles de un tipo de vehículo específico."""
    db_tipo_vehiculo = await session.get(TipoVehiculo, tipo_vehiculo_id)
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
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Actualiza los datos de un tipo de vehículo existente."""
    db_tipo_vehiculo = await session.get(TipoVehiculo, tipo_vehiculo_id)
    if not db_tipo_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de vehículo con ID {tipo_vehiculo_id} no encontrado para actualizar."
        )

    update_data = tipo_vehiculo_update.model_dump(exclude_unset=True)

    # Verificación simple de duplicado
    if "nombre" in update_data and update_data["nombre"] != db_tipo_vehiculo.nombre:
        stmt_nombre = select(TipoVehiculo).where(
            TipoVehiculo.nombre == update_data["nombre"],
            TipoVehiculo.id != tipo_vehiculo_id
        )
        result_nombre = await session.exec(stmt_nombre)
        if result_nombre.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro tipo de vehículo con el nombre '{update_data['nombre']}'"
            )

    # Aplicar actualizaciones
    for key, value in update_data.items():
        setattr(db_tipo_vehiculo, key, value)

    # Auditoría
    db_tipo_vehiculo.actualizado_en = datetime.now(timezone.utc)
    db_tipo_vehiculo.actualizado_por = current_user.id

    session.add(db_tipo_vehiculo)
    try:
        await session.commit()
        await session.refresh(db_tipo_vehiculo)
        logger.info(f"Tipo Vehículo {tipo_vehiculo_id} actualizado por {current_user.username}")
        return db_tipo_vehiculo
    except IntegrityError as e:
        await session.rollback()
        logger.warning(f"Error de integridad al actualizar tipo vehículo {tipo_vehiculo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al guardar. El nombre '{update_data.get('nombre', db_tipo_vehiculo.nombre)}' ya podría existir (insensible a mayúsculas/acentos) o hubo otro problema."
        )
    except Exception as e:
        await session.rollback()
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
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Marca un tipo de vehículo como inactivo."""
    db_tipo_vehiculo = await session.get(TipoVehiculo, tipo_vehiculo_id)
    if not db_tipo_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de vehículo con ID {tipo_vehiculo_id} no encontrado para desactivar."
        )

    if not db_tipo_vehiculo.activo:
        return # Idempotente

    db_tipo_vehiculo.activo = False
    db_tipo_vehiculo.actualizado_en = datetime.now(timezone.utc)
    db_tipo_vehiculo.actualizado_por = current_user.id

    session.add(db_tipo_vehiculo)
    try:
        await session.commit()
        logger.info(f"Tipo Vehículo {tipo_vehiculo_id} desactivado por {current_user.username}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error al desactivar tipo vehículo {tipo_vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # O 500
            detail=f"No se pudo desactivar el tipo de vehículo. Puede estar en uso por vehículos existentes. Detalle DB: {str(e)}"
        )
