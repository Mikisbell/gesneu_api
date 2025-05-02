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

import auth # Asegúrate que este módulo auth exista y tenga get_current_user
from database import get_session
from models.vehiculo import Vehiculo
from schemas.vehiculo import VehiculoCreate, VehiculoRead, VehiculoUpdate
from models.usuario import Usuario # Asumiendo que Usuario está definido

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
    current_user: Usuario = Depends(auth.get_current_user)
):
    """Crea un nuevo registro de vehículo"""
    # Verificar duplicados ANTES del try...except principal
    stmt_eco = select(Vehiculo).where(Vehiculo.numero_economico == vehiculo_in.numero_economico)
    result_eco = await session.exec(stmt_eco)
    db_vehiculo_eco = result_eco.first()
    if db_vehiculo_eco:
        # Lanza la excepción directamente, FastAPI la manejará
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe vehículo con número económico '{vehiculo_in.numero_economico}'"
        )

    if vehiculo_in.placa:
        stmt_placa = select(Vehiculo).where(Vehiculo.placa == vehiculo_in.placa)
        result_placa = await session.exec(stmt_placa)
        db_vehiculo_placa = result_placa.first()
        if db_vehiculo_placa:
            # Lanza la excepción directamente
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe vehículo con placa '{vehiculo_in.placa}'"
            )

    # Preparar datos
    vehiculo_data = vehiculo_in.model_dump(exclude_unset=True)
    vehiculo_data["creado_por"] = current_user.id
    db_vehiculo = Vehiculo.model_validate(vehiculo_data)

    # Intentar guardar en BD
    session.add(db_vehiculo)
    try:
        await session.commit()
        await session.refresh(db_vehiculo)
        logger.info(f"Vehículo {db_vehiculo.numero_economico} creado por {current_user.username}")
        return db_vehiculo
    except IntegrityError as e: # Captura específica para errores de BD al guardar
        await session.rollback()
        logger.error(f"Error de integridad (inesperado aquí?) al crear vehículo: {str(e)}", exc_info=True)
        # Si llegamos aquí, es un error de BD no detectado antes (ej. otra constraint)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al guardar el vehículo."
        )
    # --- Ya no necesitamos el except Exception general aquí ---
    # porque los errores 409 esperados se lanzan antes.

@router.get(
    "/",
    response_model=List[VehiculoRead],
    summary="Listar vehículos"
)
async def leer_vehiculos(
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(auth.get_current_user), # Asumiendo protección
    skip: int = 0,
    limit: int = Query(default=100, le=200),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo") # Default None para ver todos
):
    """Obtiene una lista de vehículos filtrados por estado"""
    # No necesita try-except complejo, la consulta es simple
    stmt = select(Vehiculo)
    if activo is not None:
        stmt = stmt.where(Vehiculo.activo == activo)
    stmt = stmt.order_by(Vehiculo.numero_economico).offset(skip).limit(limit)
    results = await session.exec(stmt)
    return results.all() # FastAPI manejará errores de DB si ocurren

@router.get(
    "/{vehiculo_id}",
    response_model=VehiculoRead,
    summary="Obtener vehículo por ID"
)
async def leer_vehiculo_por_id(
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(auth.get_current_user), # Asumiendo protección
    vehiculo_id: uuid.UUID = Path(..., description="ID único del vehículo a obtener") # '...' indica requerido
):
    """Obtiene los detalles de un vehículo específico por su ID."""
    """Obtiene los detalles de un vehículo específico"""
    # --- Quitar el try...except Exception ---
    vehiculo = await session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        # Lanza directamente, FastAPI lo maneja
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
    current_user: Usuario = Depends(auth.get_current_user) # Asumiendo protección
):
    """Actualiza los datos de un vehículo existente."""
    """Actualiza los datos de un vehículo existente"""
    # --- Misma lógica de excepción que en POST ---
    db_vehiculo = await session.get(Vehiculo, vehiculo_id)
    if not db_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado para actualizar."
        )

    update_data = vehiculo_update.model_dump(exclude_unset=True)

    # Verificar duplicados antes de intentar guardar
    if "numero_economico" in update_data and update_data["numero_economico"] != db_vehiculo.numero_economico:
        stmt_eco = select(Vehiculo).where(Vehiculo.numero_economico == update_data["numero_economico"], Vehiculo.id != vehiculo_id)
        result_eco = await session.exec(stmt_eco)
        if result_eco.first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Número económico '{update_data['numero_economico']}' ya existe.")

    if "placa" in update_data and update_data["placa"] != db_vehiculo.placa:
        stmt_placa = select(Vehiculo).where(Vehiculo.placa == update_data["placa"], Vehiculo.id != vehiculo_id)
        result_placa = await session.exec(stmt_placa)
        if result_placa.first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Placa '{update_data['placa']}' ya existe.")

    # Actualizar campos
    for key, value in update_data.items():
        setattr(db_vehiculo, key, value)
    db_vehiculo.actualizado_en = datetime.now(timezone.utc)
    db_vehiculo.actualizado_por = current_user.id

    # Intentar guardar
    session.add(db_vehiculo)
    try:
        await session.commit()
        await session.refresh(db_vehiculo)
        logger.info(f"Vehículo {vehiculo_id} actualizado por {current_user.username}")
        return db_vehiculo
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad al actualizar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al actualizar."
        )

@router.delete(
    "/{vehiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Inactivar vehículo (Eliminación lógica)"
)
async def eliminar_vehiculo(
    vehiculo_id: uuid.UUID = Path(..., description="ID del vehículo a inactivar"),
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(auth.get_current_user) # Asumiendo protección
):
    """Realiza una eliminación lógica del vehículo"""
    # --- Misma lógica de excepción que en PUT/GET ID ---
    vehiculo = await session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado para eliminar."
        )
    if not vehiculo.activo:
        return # Idempotente

    # Marcar como inactivo
    vehiculo.activo = False
    vehiculo.fecha_baja = date.today()
    vehiculo.actualizado_en = datetime.now(timezone.utc)
    vehiculo.actualizado_por = current_user.id

    # Intentar guardar
    session.add(vehiculo)
    try:
        await session.commit()
        logger.info(f"Vehículo {vehiculo_id} inactivado por {current_user.username}")
    except Exception as e: # Captura errores inesperados al guardar
        await session.rollback()
        logger.error(f"Error al inactivar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud de inactivación."
        )