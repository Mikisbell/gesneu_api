# routers/alertas.py
import uuid
import logging
from typing import List, Optional
from schemas.common import TipoAlertaEnum
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
from sqlalchemy.sql import func
from sqlmodel.ext.asyncio.session import AsyncSession

from core.dependencies import get_session, get_current_active_user
from models.usuario import Usuario
from models.alerta import Alerta
from schemas.alerta import AlertaResponse, AlertaUpdate, AlertaConDetallesResponse
from crud.crud_alerta import alerta as crud_alerta

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=List[AlertaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar alertas con filtros"
)
async def listar_alertas(
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = Query(default=100, le=200),
    resuelta: Optional[bool] = Query(default=None, description="Filtrar por estado de resolución"),
    tipo_alerta: Optional[str] = Query(default=None, description="Filtrar por tipo de alerta"),
    neumatico_id: Optional[uuid.UUID] = Query(default=None, description="Filtrar por neumático"),
    vehiculo_id: Optional[uuid.UUID] = Query(default=None, description="Filtrar por vehículo"),
    modelo_id: Optional[uuid.UUID] = Query(default=None, description="Filtrar por modelo de neumático"),
    almacen_id: Optional[uuid.UUID] = Query(default=None, description="Filtrar por almacén")
):
    """
    Lista todas las alertas con filtros opcionales.
    
    Permite filtrar por:
    - Estado de resolución (resuelta/no resuelta)
    - Tipo de alerta (PROFUNDIDAD_BAJA, STOCK_MINIMO, etc.)
    - Neumático específico
    - Vehículo específico
    - Modelo de neumático
    - Almacén
    
    Soporta paginación con skip y limit.
    """
    try:
        # Construir la consulta base
        query = select(Alerta)
        
        # Aplicar filtros si se proporcionan
        if resuelta is not None:
            query = query.where(Alerta.resuelta == resuelta)
        if tipo_alerta:
            query = query.where(Alerta.tipo_alerta == tipo_alerta)
        if neumatico_id:
            query = query.where(Alerta.neumatico_id == neumatico_id)
        if vehiculo_id:
            query = query.where(Alerta.vehiculo_id == vehiculo_id)
        if modelo_id:
            query = query.where(Alerta.modelo_id == modelo_id)
        if almacen_id:
            query = query.where(Alerta.almacen_id == almacen_id)
        
        # Ordenar por timestamp (más recientes primero)
        query = query.order_by(Alerta.creado_en.desc())
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar la consulta
        result = await session.exec(query)
        alertas = result.all()
        
        return alertas
    except Exception as e:
        logger.error(f"Error al listar alertas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener listado de alertas"
        )

@router.get(
    "/{alerta_id}",
    response_model=AlertaConDetallesResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalles de una alerta"
)
async def obtener_alerta(
    alerta_id: uuid.UUID = Path(..., description="ID único de la alerta"),
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene los detalles completos de una alerta específica por su ID.
    
    Incluye información relacionada como:
    - Detalles del neumático (si aplica)
    - Detalles del vehículo (si aplica)
    - Detalles del modelo (si aplica)
    - Detalles del almacén (si aplica)
    """
    alerta = await crud_alerta.get(session, id=alerta_id)
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerta con ID {alerta_id} no encontrada"
        )
    
    return alerta

@router.patch(
    "/{alerta_id}",
    response_model=AlertaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado de una alerta"
)
async def actualizar_alerta(
    alerta_update: AlertaUpdate,
    alerta_id: uuid.UUID = Path(..., description="ID único de la alerta a actualizar"),
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza el estado de una alerta, típicamente para marcarla como resuelta.
    
    Permite:
    - Marcar como resuelta/no resuelta
    - Añadir notas de resolución
    - Registrar quién gestionó la alerta
    """
    # Obtener la alerta existente
    alerta = await crud_alerta.get(session, id=alerta_id)
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerta con ID {alerta_id} no encontrada"
        )
    
    # Preparar datos de actualización
    update_data = alerta_update.model_dump(exclude_unset=True)
    
    # Si se está marcando como resuelta y no se proporcionó timestamp_gestion
    if update_data.get("resuelta") and not update_data.get("timestamp_gestion"):
        update_data["timestamp_gestion"] = datetime.now(timezone.utc)
    
    # Siempre registrar el usuario que actualiza la alerta
    update_data["actualizado_por"] = current_user.id
    
    # Si se está marcando como resuelta, registrar quién la gestionó
    if "resuelta" in update_data and update_data["resuelta"]:
        update_data["gestionada_por"] = current_user.id
    
    # Actualizar la alerta
    try:
        # Asegurarnos de que notas_resolucion se guarde correctamente si el campo existe
        if "notas_resolucion" in update_data:
            try:
                # Intentar actualizar directamente en el objeto de la base de datos
                alerta.notas_resolucion = update_data["notas_resolucion"]
                session.add(alerta)
                await session.commit()
                await session.refresh(alerta)
                logger.info(f"Notas de resolución actualizadas para alerta {alerta_id}")
            except Exception as e:
                # Si el campo no existe en el modelo, simplemente lo ignoramos
                logger.warning(f"No se pudo actualizar notas_resolucion: {str(e)}")
                # Eliminar del diccionario para evitar errores en la actualización posterior
                update_data.pop("notas_resolucion", None)
        
        # Continuar con la actualización normal
        updated_alerta = await crud_alerta.update(session, db_obj=alerta, obj_in=update_data)
        logger.info(f"Alerta {alerta_id} actualizada por {current_user.username}")
        
        # Asegurarnos de que la respuesta incluya las notas de resolución
        if "notas_resolucion" in update_data and not updated_alerta.notas_resolucion:
            # Si no se actualizó correctamente, hacerlo manualmente
            updated_alerta.notas_resolucion = update_data["notas_resolucion"]
            
        return updated_alerta
    except Exception as e:
        logger.error(f"Error al actualizar alerta {alerta_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la alerta"
        )

@router.get(
    "/dashboard/resumen",
    status_code=status.HTTP_200_OK,
    summary="Obtener resumen de alertas para dashboard"
)
async def obtener_resumen_alertas(
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Proporciona un resumen de alertas para mostrar en un dashboard.
    
    Incluye:
    - Conteo de alertas por tipo
    - Conteo de alertas resueltas vs no resueltas
    - Alertas recientes (últimas 10)
    """
    try:
        # Contar alertas no resueltas por tipo
        query_por_tipo = select(
            Alerta.tipo_alerta, 
            func.count(Alerta.id).label("total")
        ).where(
            Alerta.resuelta == False
        ).group_by(
            Alerta.tipo_alerta
        )
        result_por_tipo = await session.exec(query_por_tipo)
        # Convertir los valores a TipoAlertaEnum para evitar warnings de serialización
        # Primero intentamos convertir a enum, si falla usamos el valor original como string
        conteo_por_tipo = {}
        for tipo, total in result_por_tipo:
            try:
                # Intentar convertir a enum
                enum_tipo = TipoAlertaEnum(tipo)
                conteo_por_tipo[enum_tipo] = total
            except ValueError:
                # Si no es un valor válido del enum, usar el string
                conteo_por_tipo[str(tipo)] = total
        
        # Contar total de alertas resueltas vs no resueltas
        query_por_estado = select(
            Alerta.resuelta, 
            func.count(Alerta.id).label("total")
        ).group_by(
            Alerta.resuelta
        )
        result_por_estado = await session.exec(query_por_estado)
        conteo_por_estado = {str(resuelta): total for resuelta, total in result_por_estado}
        
        # Obtener las 10 alertas más recientes no resueltas
        query_recientes = select(Alerta).where(
            Alerta.resuelta == False
        ).order_by(
            Alerta.creado_en.desc()
        ).limit(10)
        result_recientes = await session.exec(query_recientes)
        alertas_obj = result_recientes.all()
        
        # Convertir las alertas a diccionarios para evitar problemas de serialización
        alertas_recientes = []
        for alerta in alertas_obj:
            # Convertir el tipo_alerta a enum si es posible
            try:
                tipo_alerta = TipoAlertaEnum(alerta.tipo_alerta)
            except ValueError:
                tipo_alerta = alerta.tipo_alerta
                
            alertas_recientes.append({
                "id": str(alerta.id),
                "tipo_alerta": tipo_alerta,
                "descripcion": alerta.descripcion,
                "nivel_severidad": alerta.nivel_severidad,
                "resuelta": alerta.resuelta,
                "creado_en": alerta.creado_en.isoformat() if alerta.creado_en else None
            })
        
        return {
            "conteo_por_tipo": conteo_por_tipo,
            "conteo_por_estado": conteo_por_estado,
            "alertas_recientes": alertas_recientes
        }
    except Exception as e:
        logger.error(f"Error al obtener resumen de alertas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener resumen de alertas para dashboard"
        )
