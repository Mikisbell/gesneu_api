# routers/neumaticos_router.py
import uuid
import logging
from datetime import datetime
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import get_session
from models.usuario import Usuario
from models.neumatico import Neumatico, EstadoNeumaticoEnum  # Importar Enum
from models.evento_neumatico import EventoNeumatico
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoRead
from schemas.neumatico import HistorialNeumaticoItem, NeumaticoInstaladoItem
import auth

router = APIRouter(tags=["Neumáticos y Eventos"])
logger = logging.getLogger(__name__)

@router.post(
    "/eventos",
    response_model=EventoNeumaticoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo evento para neumático",
    description="Crea un nuevo evento relacionado con el ciclo de vida de un neumático"
)
async def crear_evento_neumatico(
    evento: EventoNeumaticoCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[Usuario, Depends(auth.get_current_active_user)]
):
    """Registra un nuevo evento para un neumático"""
    try:
        db_evento = EventoNeumatico.model_validate(
            evento, 
            update={"usuario_id": current_user.id}
        )
        
        session.add(db_evento)
        await session.commit()
        await session.refresh(db_evento)
        
        logger.info(
            f"Evento {db_evento.tipo_evento} creado para neumático "
            f"{db_evento.neumatico_id} por usuario {current_user.username}"
        )
        return db_evento

    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad: {str(e)}", exc_info=True)
        detail_msg = "Error de datos: "
        if "foreign key" in str(e).lower():
            detail_msg += "Referencia a recurso no existente"
        elif "unique constraint" in str(e).lower():
            detail_msg += "Registro duplicado"
        else:
            detail_msg += str(e.orig)
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail_msg
        )

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Error de base de datos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de operación en base de datos"
        )

    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# routers/neumaticos_router.py
# ... (imports previos se mantienen igual)

@router.get("/{neumatico_id}/historial", response_model=List[HistorialNeumaticoItem])
async def leer_historial_neumatico(
    neumatico_id: uuid.UUID = Path(..., description="ID del neumático"),
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Obtiene el historial de eventos de un neumático"""
    try:
        stmt = select(EventoNeumatico).where(
            EventoNeumatico.neumatico_id == neumatico_id
        ).order_by(EventoNeumatico.timestamp_evento.desc())

        result = await session.exec(stmt)
        eventos = result.all()
        
        if not eventos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró historial para el neumático"
            )
        
        return [HistorialNeumaticoItem.model_validate(evento) for evento in eventos]  # <--- Corrección aquí
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el historial"
        )

@router.get("/instalados", response_model=List[NeumaticoInstaladoItem])
async def leer_neumaticos_instalados(
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Lista de neumáticos instalados"""
    try:
        stmt = select(Neumatico).where(
            Neumatico.estado_actual == EstadoNeumaticoEnum.INSTALADO
        ).order_by(
            Neumatico.fabricante,
            Neumatico.nombre_modelo
        )

        result = await session.exec(stmt)
        neumaticos = result.all()
        
        if not neumaticos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron neumáticos instalados"
            )
        
        return [NeumaticoInstaladoItem.model_validate(n) for n in neumaticos]  # <--- Corrección aquí
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar neumáticos instalados"
        )