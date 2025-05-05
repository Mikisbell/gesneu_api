# routers/proveedores.py (Corregido - Sin Prefijo Interno)
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

# Dependencias y modelos/schemas necesarios
import auth # Para la autenticación/autorización
from database import get_session
from models.proveedor import Proveedor
from models.usuario import Usuario # Para obtener el current_user
from schemas.proveedor import ProveedorCreate, ProveedorRead, ProveedorUpdate

# Crear el router específico para proveedores
# --- CORRECCIÓN: Eliminar el argumento prefix ---
router = APIRouter(
    tags=["Proveedores"], # Etiqueta para la documentación de Swagger UI
    dependencies=[Depends(auth.get_current_active_user)] # Proteger todos los endpoints
)
# --- FIN CORRECCIÓN ---

logger = logging.getLogger(__name__)

# El resto del código (endpoints @router.post, @router.get, etc.) permanece igual
# ... (pega aquí el resto de tu código original para este archivo) ...

@router.post(
    "/", # Ruta relativa: POST /proveedores/
    response_model=ProveedorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proveedor"
)
async def crear_proveedor(
    proveedor_in: ProveedorCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user) # Ya incluido en dependencies
):
    """Crea un nuevo registro de proveedor en la base de datos."""
    # Verificar duplicado por nombre (ajusta si necesitas unicidad por otro campo)
    stmt_nombre = select(Proveedor).where(Proveedor.nombre == proveedor_in.nombre)
    result_nombre = await session.exec(stmt_nombre)
    if result_nombre.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un proveedor con el nombre '{proveedor_in.nombre}'"
        )

    # Preparar datos y crear instancia del modelo
    proveedor_data = proveedor_in.model_dump()
    db_proveedor = Proveedor.model_validate(proveedor_data)
    db_proveedor.creado_por = current_user.id # Auditoría

    # Guardar en BD
    session.add(db_proveedor)
    try:
        await session.commit()
        await session.refresh(db_proveedor)
        logger.info(f"Proveedor '{db_proveedor.nombre}' creado por {current_user.username}")
        return db_proveedor
    except IntegrityError as e: # Captura errores de BD al guardar
        await session.rollback()
        logger.error(f"Error de integridad al crear proveedor: {str(e)}", exc_info=True)
        # Podría ser un duplicado no detectado antes u otra constraint
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al guardar el proveedor."
        )
    except Exception as e:
         await session.rollback()
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
    # current_user: Usuario = Depends(auth.get_current_active_user) # Ya protegido a nivel router
):
    """Obtiene una lista paginada de proveedores, opcionalmente filtrada por estado."""
    statement = select(Proveedor)
    if activo is not None:
        statement = statement.where(Proveedor.activo == activo)

    statement = statement.order_by(Proveedor.nombre).offset(skip).limit(limit)

    results = await session.exec(statement)
    proveedores = results.all()
    return proveedores


@router.get(
    "/{proveedor_id}", # Ruta relativa: GET /proveedores/{proveedor_id}
    response_model=ProveedorRead,
    summary="Obtener proveedor por ID"
)
async def leer_proveedor_por_id(
    proveedor_id: uuid.UUID = Path(..., description="ID único del proveedor a obtener"),
    session: AsyncSession = Depends(get_session)
    # current_user: Usuario = Depends(auth.get_current_active_user) # Ya protegido
):
    """Obtiene los detalles de un proveedor específico por su ID."""
    db_proveedor = await session.get(Proveedor, proveedor_id)
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
    current_user: Usuario = Depends(auth.get_current_active_user) # Necesitamos user para auditoría
):
    """Actualiza los datos de un proveedor existente."""
    db_proveedor = await session.get(Proveedor, proveedor_id)
    if not db_proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {proveedor_id} no encontrado para actualizar."
        )

    update_data = proveedor_update.model_dump(exclude_unset=True) # Solo campos enviados

    # Verificar duplicado por nombre si se está cambiando
    if "nombre" in update_data and update_data["nombre"] != db_proveedor.nombre:
        stmt_nombre = select(Proveedor).where(
            Proveedor.nombre == update_data["nombre"],
            Proveedor.id != proveedor_id # Excluir el proveedor actual
        )
        result_nombre = await session.exec(stmt_nombre)
        if result_nombre.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro proveedor con el nombre '{update_data['nombre']}'"
            )

    # Aplicar actualizaciones
    for key, value in update_data.items():
        setattr(db_proveedor, key, value)

    # Auditoría
    db_proveedor.actualizado_en = datetime.now(timezone.utc)
    db_proveedor.actualizado_por = current_user.id

    session.add(db_proveedor)
    try:
        await session.commit()
        await session.refresh(db_proveedor)
        logger.info(f"Proveedor {proveedor_id} actualizado por {current_user.username}")
        return db_proveedor
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Error de integridad al actualizar proveedor {proveedor_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos al actualizar proveedor."
        )
    except Exception as e:
        await session.rollback()
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
    current_user: Usuario = Depends(auth.get_current_active_user) # Necesitamos user para auditoría
):
    """Marca un proveedor como inactivo (eliminación lógica)."""
    db_proveedor = await session.get(Proveedor, proveedor_id)
    if not db_proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {proveedor_id} no encontrado para desactivar."
        )

    if not db_proveedor.activo:
        # Ya está inactivo, no hacer nada (idempotente)
        return # Devuelve 204 implícitamente

    # Marcar como inactivo y auditoría
    db_proveedor.activo = False
    db_proveedor.actualizado_en = datetime.now(timezone.utc)
    db_proveedor.actualizado_por = current_user.id

    session.add(db_proveedor)
    try:
        await session.commit()
        logger.info(f"Proveedor {proveedor_id} desactivado por {current_user.username}")
        # No se devuelve contenido en 204
    except Exception as e:
        await session.rollback()
        logger.error(f"Error al desactivar proveedor {proveedor_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al desactivar proveedor."
        )
