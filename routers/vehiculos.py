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
    session: AsyncSession = Depends(get_session), # Recibe sesión SQLModel
    current_user: Usuario = Depends(auth.get_current_user) # Asegurar que get_current_user funcione
):
    """Crea un nuevo registro de vehículo"""
    try:
        # --- Usar session.exec() ---
        stmt_eco = select(Vehiculo).where(Vehiculo.numero_economico == vehiculo_in.numero_economico)
        result_eco = await session.exec(stmt_eco) # <--- Usar exec()
        db_vehiculo_eco = result_eco.first()
        if db_vehiculo_eco:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe vehículo con número económico '{vehiculo_in.numero_economico}'"
            )

        if vehiculo_in.placa:
            stmt_placa = select(Vehiculo).where(Vehiculo.placa == vehiculo_in.placa)
            result_placa = await session.exec(stmt_placa) # <--- Usar exec()
            db_vehiculo_placa = result_placa.first()
            if db_vehiculo_placa:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe vehículo con placa '{vehiculo_in.placa}'"
                )

        # Convertir schema a diccionario, excluyendo valores no seteados
        # y añadiendo el usuario que crea
        vehiculo_data = vehiculo_in.model_dump(exclude_unset=True)
        # Asegúrate que tu modelo Usuario tenga un campo 'id'
        vehiculo_data["creado_por"] = current_user.id

        db_vehiculo = Vehiculo.model_validate(vehiculo_data) # Usar model_validate para SQLModel >= 0.0.14
        # O si usas una versión anterior: db_vehiculo = Vehiculo(**vehiculo_data)

        session.add(db_vehiculo)
        await session.commit()
        await session.refresh(db_vehiculo)

        logger.info(f"Vehículo {db_vehiculo.numero_economico} creado por {current_user.username}")
        return db_vehiculo

    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad al crear vehículo: {str(e)}", exc_info=True)
        # Puedes intentar dar un mensaje más específico si detectas la columna/constraint
        detail = "Error de datos: Ya existe un vehículo con datos únicos conflictivos (placa, VIN, etc.)."
        # Comprobación básica (puede necesitar ajuste según tu DB exacta)
        if "numero_economico" in str(e).lower():
             detail = f"Ya existe vehículo con número económico '{vehiculo_in.numero_economico}'"
        elif "placa" in str(e).lower() and vehiculo_in.placa:
             detail = f"Ya existe vehículo con placa '{vehiculo_in.placa}'"
        elif "vin" in str(e).lower() and vehiculo_in.vin:
             detail = f"Ya existe vehículo con VIN '{vehiculo_in.vin}'"

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado al crear vehículo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear vehículo."
        )

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
    """Obtiene una lista de vehículos, opcionalmente filtrados por estado activo."""
    try:
        stmt = select(Vehiculo)
        if activo is not None:
            stmt = stmt.where(Vehiculo.activo == activo)

        # Ordenar consistentemente, por ejemplo por numero_economico
        stmt = stmt.order_by(Vehiculo.numero_economico).offset(skip).limit(limit)

        # --- Usar session.exec() ---
        results = await session.exec(stmt) # <--- Usar exec()
        vehiculos = results.all()
        return vehiculos
    except Exception as e:
        logger.error(f"Error al listar vehículos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al listar vehículos."
        )

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
    try:
        # session.get() funciona igual para ambas sesiones
        vehiculo = await session.get(Vehiculo, vehiculo_id)
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehículo con ID {vehiculo_id} no encontrado."
            )
        return vehiculo
    except Exception as e:
        # Evitar exponer detalles internos en producción
        logger.error(f"Error al obtener vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener vehículo."
        )


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
    try:
        db_vehiculo = await session.get(Vehiculo, vehiculo_id)
        if not db_vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehículo con ID {vehiculo_id} no encontrado para actualizar."
            )

        # Obtener datos del schema de actualización, excluyendo los no enviados
        update_data = vehiculo_update.model_dump(exclude_unset=True)

        # Verificar si se intenta actualizar placa o numero_economico a uno existente
        if "numero_economico" in update_data and update_data["numero_economico"] != db_vehiculo.numero_economico:
             stmt_eco = select(Vehiculo).where(
                 Vehiculo.numero_economico == update_data["numero_economico"],
                 Vehiculo.id != vehiculo_id # Excluir el propio vehículo
             )
             result_eco = await session.exec(stmt_eco) # <--- Usar exec()
             if result_eco.first():
                 raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Número económico '{update_data['numero_economico']}' ya existe.")

        if "placa" in update_data and update_data["placa"] != db_vehiculo.placa:
             stmt_placa = select(Vehiculo).where(
                 Vehiculo.placa == update_data["placa"],
                 Vehiculo.id != vehiculo_id # Excluir el propio vehículo
             )
             result_placa = await session.exec(stmt_placa) # <--- Usar exec()
             if result_placa.first():
                 raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Placa '{update_data['placa']}' ya existe.")

        # Actualizar campos permitidos
        for key, value in update_data.items():
            setattr(db_vehiculo, key, value)

        # Actualizar campos de auditoría
        db_vehiculo.actualizado_en = datetime.now(timezone.utc)
        db_vehiculo.actualizado_por = current_user.id # Asumiendo que current_user tiene id

        session.add(db_vehiculo)
        await session.commit()
        await session.refresh(db_vehiculo)

        logger.info(f"Vehículo {vehiculo_id} actualizado por {current_user.username}")
        return db_vehiculo

    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad al actualizar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al actualizar. Verifique campos únicos (placa, VIN, etc.)."
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error al actualizar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
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
    current_user: Usuario = Depends(auth.get_current_user) # Asumiendo protección
):
    """
    Realiza una eliminación lógica del vehículo (lo marca como inactivo).
    No elimina el registro de la base de datos.
    """
    try:
        vehiculo = await session.get(Vehiculo, vehiculo_id)
        if not vehiculo:
            # Es idempotente, si no existe, no hacemos nada o retornamos 404
            # Devolver 404 es más informativo
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehículo con ID {vehiculo_id} no encontrado para eliminar."
            )

        # Si ya está inactivo, no hacer nada (idempotencia)
        if not vehiculo.activo:
             # Podríamos devolver 204 directamente o quizás un 304 Not Modified,
             # pero 204 es simple y común para DELETE exitosos.
             return # Ya está inactivo

        # Marcar como inactivo y registrar auditoría
        vehiculo.activo = False
        vehiculo.fecha_baja = date.today() # Registrar fecha de baja
        vehiculo.actualizado_en = datetime.now(timezone.utc)
        vehiculo.actualizado_por = current_user.id

        session.add(vehiculo)
        await session.commit()
        # No necesitamos refresh aquí ya que no devolvemos el objeto

        logger.info(f"Vehículo {vehiculo_id} inactivado (eliminación lógica) por {current_user.username}")
        # No se devuelve contenido en un 204

    except Exception as e:
        await session.rollback()
        logger.error(f"Error al inactivar vehículo {vehiculo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al inactivar vehículo."
        )