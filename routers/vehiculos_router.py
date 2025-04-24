# routers/vehiculos_router.py (Corregido para Refactorización v3)
import uuid
from datetime import date, datetime, timezone
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

# --- Importaciones Corregidas ---
import auth
from database import get_session
# Modelos específicos desde sus nuevas ubicaciones
from models.vehiculo import Vehiculo           # Modelo de TABLA Vehiculo
from schemas.vehiculo import VehiculoCreate, VehiculoRead, VehiculoUpdate # Schemas API
from models.usuario import Usuario             # Modelo de TABLA Usuario (para current_user)
# --- Fin Importaciones Corregidas ---


router = APIRouter()

@router.post("/", response_model=VehiculoRead, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo vehículo")
async def crear_vehiculo(
    vehiculo_in: VehiculoCreate, # <-- Usa Schema Create
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[Usuario, Depends(auth.get_current_active_user)] # <-- Usa Modelo Usuario
):
    """ Crea un nuevo registro de vehículo... """
    # Verificar duplicados usando el modelo de tabla Vehiculo
    statement_eco = select(Vehiculo).where(Vehiculo.numero_economico == vehiculo_in.numero_economico)
    results_eco = await session.exec(statement_eco)
    if results_eco.first():
        raise HTTPException(status_code=409, detail=f"Ya existe vehículo con número económico '{vehiculo_in.numero_economico}'.")
    if vehiculo_in.placa:
        statement_placa = select(Vehiculo).where(Vehiculo.placa == vehiculo_in.placa)
        results_placa = await session.exec(statement_placa)
        if results_placa.first():
             raise HTTPException(status_code=409, detail=f"Ya existe vehículo con placa '{vehiculo_in.placa}'.")

    try:
        vehiculo_data = vehiculo_in.model_dump(exclude_unset=True)
        vehiculo_data["creado_por"] = current_user.id
        db_vehiculo = Vehiculo(**vehiculo_data) # <-- Crea instancia de Tabla Vehiculo
        session.add(db_vehiculo)
        await session.commit()
        await session.refresh(db_vehiculo)
        return db_vehiculo # FastAPI usa VehiculoRead para respuesta
    except IntegrityError as e: # ... (manejo de errores sin cambios, usa vehiculo_in) ...
        await session.rollback(); detail = "..."; raise HTTPException(...)
    except Exception as e: # ... (manejo de errores sin cambios) ...
        await session.rollback(); raise HTTPException(...)

@router.get("/", response_model=List[VehiculoRead], summary="Listar vehículos") # <-- Usa Schema Read
async def leer_vehiculos(
    *, session: Annotated[AsyncSession, Depends(get_session)], current_user: Annotated[Usuario, Depends(auth.get_current_active_user)], # <-- Usa Modelo Usuario
    skip: int = 0, limit: int = Query(default=100, le=200), activo: Optional[bool] = Query(default=True)
):
    """ Obtiene una lista de vehículos... """
    statement = select(Vehiculo) # <-- Usa Modelo Tabla Vehiculo
    if activo is not None: statement = statement.where(Vehiculo.activo == activo)
    statement = statement.order_by(Vehiculo.numero_economico).offset(skip).limit(limit)
    results = await session.exec(statement)
    vehiculos = results.all()
    return vehiculos # FastAPI usa Lista de VehiculoRead

@router.get("/{vehiculo_id}", response_model=VehiculoRead, summary="Obtener un vehículo por ID") # <-- Usa Schema Read
async def leer_vehiculo_por_id(
    *, session: Annotated[AsyncSession, Depends(get_session)], current_user: Annotated[Usuario, Depends(auth.get_current_active_user)], # <-- Usa Modelo Usuario
    vehiculo_id: uuid.UUID = Path(description="ID del vehículo a obtener")
):
    """ Obtiene los detalles de un vehículo específico... """
    db_vehiculo = await session.get(Vehiculo, vehiculo_id) # <-- Usa Modelo Tabla Vehiculo
    if not db_vehiculo: raise HTTPException(status_code=404, detail=f"Vehículo con id {vehiculo_id} no encontrado")
    return db_vehiculo # FastAPI usa VehiculoRead

@router.put("/{vehiculo_id}", response_model=VehiculoRead, summary="Actualizar un vehículo existente") # <-- Usa Schema Read
async def actualizar_vehiculo(
    *, session: Annotated[AsyncSession, Depends(get_session)], current_user: Annotated[Usuario, Depends(auth.get_current_active_user)], # <-- Usa Modelo Usuario
    vehiculo_id: uuid.UUID = Path(description="ID del vehículo a actualizar"),
    vehiculo_update: VehiculoUpdate # <-- Usa Schema Update
):
    """ Actualiza los datos de un vehículo existente... """
    db_vehiculo = await session.get(Vehiculo, vehiculo_id) # <-- Usa Modelo Tabla Vehiculo
    if not db_vehiculo: raise HTTPException(status_code=404, detail=f"Vehículo con id {vehiculo_id} no encontrado")
    update_data = vehiculo_update.model_dump(exclude_unset=True)
    # ... (Validación de duplicados usa Modelo Tabla Vehiculo) ...
    db_vehiculo.sqlmodel_update(update_data) # Actualiza el objeto de tabla
    db_vehiculo.actualizado_en = datetime.now(timezone.utc)
    db_vehiculo.actualizado_por = current_user.id
    try: # ... (commit, refresh, error handling sin cambios) ...
        session.add(db_vehiculo); await session.commit(); await session.refresh(db_vehiculo); return db_vehiculo
    except IntegrityError as e: await session.rollback(); detail = "..."; raise HTTPException(...)
    except Exception as e: await session.rollback(); raise HTTPException(...)

@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar (Inactivar) un vehículo por ID")
async def eliminar_vehiculo(
    *, session: Annotated[AsyncSession, Depends(get_session)], current_user: Annotated[Usuario, Depends(auth.get_current_active_user)], # <-- Usa Modelo Usuario
    vehiculo_id: uuid.UUID = Path(description="ID del vehículo a inactivar")
):
    """ Realiza una eliminación lógica... """
    db_vehiculo = await session.get(Vehiculo, vehiculo_id) # <-- Usa Modelo Tabla Vehiculo
    if not db_vehiculo: raise HTTPException(status_code=404, detail=f"Vehículo con id {vehiculo_id} no encontrado")
    if not db_vehiculo.activo: return None
    db_vehiculo.activo = False; db_vehiculo.fecha_baja = date.today(); db_vehiculo.actualizado_en = datetime.now(timezone.utc); db_vehiculo.actualizado_por = current_user.id
    try: # ... (commit, error handling sin cambios) ...
        session.add(db_vehiculo); await session.commit(); return None
    except Exception as e: await session.rollback(); raise HTTPException(...)