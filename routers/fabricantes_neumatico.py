# routers/fabricantes_neumatico.py
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

# Dependencias y modelos/schemas necesarios
import auth
from database import get_session
from models.fabricante import FabricanteNeumatico # El modelo
from models.usuario import Usuario
# Importar los schemas
from schemas.fabricante import (
    FabricanteNeumaticoCreate,
    FabricanteNeumaticoRead,
    FabricanteNeumaticoUpdate
)

# Crear el router específico
router = APIRouter(
    prefix="/fabricantes", # Usamos un prefijo claro
    tags=["Fabricantes de Neumáticos"],
    dependencies=[Depends(auth.get_current_active_user)]
)

logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=FabricanteNeumaticoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo fabricante de neumáticos"
)
async def crear_fabricante(
    fabricante_in: FabricanteNeumaticoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Crea un nuevo registro de fabricante de neumáticos."""
    # Verificación simple de duplicados (nombre y código)
    # La BD puede tener índices más complejos (lower, unaccent, etc.)
    stmt_nombre = select(FabricanteNeumatico).where(FabricanteNeumatico.nombre == fabricante_in.nombre)
    result_nombre = await session.exec(stmt_nombre)
    if result_nombre.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un fabricante con el nombre '{fabricante_in.nombre}'"
        )

    if fabricante_in.codigo_abreviado:
         stmt_codigo = select(FabricanteNeumatico).where(FabricanteNeumatico.codigo_abreviado == fabricante_in.codigo_abreviado)
         result_codigo = await session.exec(stmt_codigo)
         if result_codigo.first():
             raise HTTPException(
                 status_code=status.HTTP_409_CONFLICT,
                 detail=f"Ya existe un fabricante con el código '{fabricante_in.codigo_abreviado}'"
             )

    # Crear instancia y auditoría
    fabricante_data = fabricante_in.model_dump()
    db_fabricante = FabricanteNeumatico.model_validate(fabricante_data)
    db_fabricante.creado_por = current_user.id

    # Guardar en BD
    session.add(db_fabricante)
    try:
        await session.commit()
        await session.refresh(db_fabricante)
        logger.info(f"Fabricante '{db_fabricante.nombre}' creado por {current_user.username}")
        return db_fabricante
    except IntegrityError as e:
        await session.rollback()
        logger.warning(f"Error de integridad al crear fabricante (posible duplicado BD): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al guardar. El nombre o código ya podría existir (verificar mayúsculas/acentos si aplica) o hubo otro problema."
        )
    except Exception as e:
         await session.rollback()
         logger.error(f"Error inesperado al crear fabricante: {str(e)}", exc_info=True)
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail="Error interno al crear el fabricante."
         )

@router.get(
    "/",
    response_model=List[FabricanteNeumaticoRead],
    summary="Listar fabricantes de neumáticos"
)
async def leer_fabricantes(
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo")
):
    """Obtiene una lista paginada de fabricantes."""
    statement = select(FabricanteNeumatico)
    if activo is not None:
        statement = statement.where(FabricanteNeumatico.activo == activo)
    statement = statement.order_by(FabricanteNeumatico.nombre).offset(skip).limit(limit)
    results = await session.exec(statement)
    fabricantes = results.all()
    return fabricantes

@router.get(
    "/{fabricante_id}",
    response_model=FabricanteNeumaticoRead,
    summary="Obtener fabricante por ID"
)
async def leer_fabricante_por_id(
    fabricante_id: uuid.UUID = Path(..., description="ID único del fabricante"),
    session: AsyncSession = Depends(get_session)
):
    """Obtiene los detalles de un fabricante específico."""
    db_fabricante = await session.get(FabricanteNeumatico, fabricante_id)
    if not db_fabricante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fabricante con ID {fabricante_id} no encontrado."
        )
    return db_fabricante

@router.put(
    "/{fabricante_id}",
    response_model=FabricanteNeumaticoRead,
    summary="Actualizar un fabricante"
)
async def actualizar_fabricante(
    fabricante_id: uuid.UUID,
    fabricante_update: FabricanteNeumaticoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Actualiza los datos de un fabricante existente."""
    db_fabricante = await session.get(FabricanteNeumatico, fabricante_id)
    if not db_fabricante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fabricante con ID {fabricante_id} no encontrado para actualizar."
        )

    update_data = fabricante_update.model_dump(exclude_unset=True)

    # Verificación simple de duplicados si se cambian
    if "nombre" in update_data and update_data["nombre"] != db_fabricante.nombre:
        stmt_nombre = select(FabricanteNeumatico).where(
            FabricanteNeumatico.nombre == update_data["nombre"],
            FabricanteNeumatico.id != fabricante_id
        )
        if (await session.exec(stmt_nombre)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, f"Nombre '{update_data['nombre']}' ya existe.")

    if "codigo_abreviado" in update_data and update_data["codigo_abreviado"] != db_fabricante.codigo_abreviado:
        if update_data["codigo_abreviado"]: # Solo si no es None/vacío
             stmt_codigo = select(FabricanteNeumatico).where(
                 FabricanteNeumatico.codigo_abreviado == update_data["codigo_abreviado"],
                 FabricanteNeumatico.id != fabricante_id
             )
             if (await session.exec(stmt_codigo)).first():
                  raise HTTPException(status.HTTP_409_CONFLICT, f"Código '{update_data['codigo_abreviado']}' ya existe.")

    # Aplicar actualizaciones
    for key, value in update_data.items():
        setattr(db_fabricante, key, value)

    # Auditoría
    db_fabricante.actualizado_en = datetime.now(timezone.utc)
    db_fabricante.actualizado_por = current_user.id

    session.add(db_fabricante)
    try:
        await session.commit()
        await session.refresh(db_fabricante)
        logger.info(f"Fabricante {fabricante_id} actualizado por {current_user.username}")
        return db_fabricante
    except IntegrityError as e:
        await session.rollback()
        logger.warning(f"Error de integridad al actualizar fabricante {fabricante_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al guardar. El nombre o código ya podría existir o hubo otro problema."
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inesperado al actualizar fabricante {fabricante_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar el fabricante."
        )

@router.delete(
    "/{fabricante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar un fabricante (Eliminación lógica)"
)
async def desactivar_fabricante(
    fabricante_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    """Marca un fabricante como inactivo."""
    db_fabricante = await session.get(FabricanteNeumatico, fabricante_id)
    if not db_fabricante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fabricante con ID {fabricante_id} no encontrado para desactivar."
        )

    # Podríamos verificar si tiene modelos asociados antes de desactivar?
    # Depende de las reglas de negocio. Por ahora, desactivamos.
    if not db_fabricante.activo:
        return # Idempotente

    db_fabricante.activo = False
    db_fabricante.actualizado_en = datetime.now(timezone.utc)
    db_fabricante.actualizado_por = current_user.id

    session.add(db_fabricante)
    try:
        await session.commit()
        logger.info(f"Fabricante {fabricante_id} desactivado por {current_user.username}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error al desactivar fabricante {fabricante_id}: {str(e)}", exc_info=True)
        # Asumiendo que errores aquí son del servidor, no por FKs (a menos que se añadan)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al desactivar el fabricante."
        )