# routers/neumaticos_router.py (Imports VERIFICADOS Y COMPLETOS)

import uuid
from typing import List, Annotated, Optional
from datetime import date, datetime, timezone # Asegurar los necesarios
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# --- Imports de nuestros módulos ---
import auth                             # auth.py
from database import get_session      # database.py

# --- Imports DESDE los nuevos directorios models/ y schemas/ ---
from models.usuario import Usuario      # Desde models/usuario.py
from models.neumatico import Neumatico  # Desde models/neumatico.py
from models.evento_neumatico import EventoNeumatico # Desde models/evento_neumatico.py

from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead # Desde schemas/evento_neumatico.py
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem  # Desde schemas/neumatico.py
# --- Fin Imports ---


# --- Definición del Router (sin cambios) ---
router = APIRouter(
    tags=["Neumáticos y Eventos"]
)

# --- Endpoints (@router.post, @router.get...) ---
# Asegúrate de que dentro de las funciones ya NO usas 'db_models.'
# Ejemplo en crear_evento_neumatico:
#   evento: EventoNeumaticoCreate,
#   current_user: Annotated[Usuario, ...]
#   db_evento = EventoNeumatico.model_validate(...)
#   response_model=EventoNeumaticoRead
# Ejemplo en leer_historial_neumatico:
#   current_user: Annotated[Usuario, ...]
#   response_model=List[HistorialNeumaticoItem]
#   historial = [HistorialNeumaticoItem(**row)...]
# Ejemplo en leer_neumaticos_instalados:
#   current_user: Annotated[Usuario, ...]
#   response_model=List[NeumaticoInstaladoItem]
#   instalados = [NeumaticoInstaladoItem(**row)...]

# ... (resto de las funciones/endpoints) ...

# --- Faltaría CRUD para Neumáticos Base, GET Inventario, etc. ---


router = APIRouter(
    # El prefijo /api/v1 se define en main.py
    tags=["Neumáticos y Eventos"]
)

@router.post("/eventos", response_model=EventoNeumaticoRead, status_code=status.HTTP_201_CREATED) # <-- Usa Schema Read
async def crear_evento_neumatico(
    evento: EventoNeumaticoCreate, # <-- Usa Schema Create
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[Usuario, Depends(auth.get_current_active_user)] # <-- Usa Modelo Usuario
):
    """ Registra un nuevo evento para un neumático... """
    try:
        # Usa el modelo de TABLA EventoNeumatico para crear la instancia
        db_evento = EventoNeumatico.model_validate(evento, update={'usuario_id': current_user.id})

        session.add(db_evento)
        await session.commit()
        await session.refresh(db_evento)
        return db_evento # FastAPI usa EventoNeumaticoRead
    except IntegrityError as e: # ... (manejo de errores sin cambios, usa evento.) ...
         await session.rollback(); detail = "..."; raise HTTPException(...)
    except Exception as e: # ... (manejo de errores sin cambios) ...
         await session.rollback(); raise HTTPException(...)

@router.get("/{neumatico_id}/historial", response_model=List[HistorialNeumaticoItem]) # <-- Usa Schema Vista
async def leer_historial_neumatico(
    *, session: Annotated[AsyncSession, Depends(get_session)], current_user: Annotated[Usuario, Depends(auth.get_current_active_user)], # <-- Usa Modelo Usuario
    neumatico_id: uuid.UUID = Path(description="ID del neumático para ver su historial")
):
    """ Obtiene el historial de eventos... """
    # Query a la vista usando text()
    statement = select(text("evento_id, tipo_evento, ...")).select_from(text("public.vw_historial_neumaticos")).where(text("neumatico_id = :nid")).order_by(text("timestamp_evento DESC"))
    results = await session.exec(statement, {"nid": neumatico_id})
    historial_raw = results.mappings().all()
    try:
        # Validar respuesta contra schema de vista
        historial = [HistorialNeumaticoItem(**row) for row in historial_raw] # <-- Usa Schema Vista
        return historial
    except Exception as e: raise HTTPException(...) # Manejar error

@router.get("/instalados", response_model=List[NeumaticoInstaladoItem]) # <-- Usa Schema Vista
async def leer_neumaticos_instalados(
    *, session: Annotated[AsyncSession, Depends(get_session)], current_user: Annotated[Usuario, Depends(auth.get_current_active_user)] # <-- Usa Modelo Usuario
):
    """ Obtiene la lista de neumáticos instalados... """
    # Query a la vista usando text()
    statement = select(text("neumatico_id, numero_serie, ...")).select_from(text("public.vw_neumaticos_instalados_optimizada")).order_by(text("fabricante, nombre_modelo"))
    results = await session.exec(statement)
    instalados_raw = results.mappings().all()
    try:
        # Validar respuesta contra schema de vista
        instalados = [NeumaticoInstaladoItem(**row) for row in instalados_raw] # <-- Usa Schema Vista
        return instalados
    except Exception as e: raise HTTPException(...) # Manejar error

# --- Faltaría CRUD para Neumáticos Base, GET Inventario, etc. ---