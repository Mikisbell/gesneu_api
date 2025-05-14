# routers/fabricantes_neumatico.py (FINAL - Sin Prefijo Interno)
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

# Dependencias y modelos/schemas necesarios
from core.dependencies import get_session # Usar la dependencia centralizada
from core.dependencies import get_current_active_user # Usar la dependencia centralizada
from models.fabricante import FabricanteNeumatico # El modelo
from models.usuario import Usuario
# Importar los schemas
from schemas.fabricante import (
    FabricanteNeumaticoCreate,
    FabricanteNeumaticoRead,
    FabricanteNeumaticoUpdate
)
# Importar el objeto CRUD
from crud.crud_fabricante import fabricante as crud_fabricante

# --- CORRECCIÓN FINAL: Eliminar el argumento prefix ---
router = APIRouter(
    tags=["Fabricantes de Neumáticos"], # Mantener tags
    dependencies=[Depends(get_current_active_user)] # Usar la dependencia centralizada
)
# --- FIN CORRECCIÓN FINAL ---

logger = logging.getLogger(__name__)

@router.post(
    "/", # La ruta relativa sigue siendo "/"
    response_model=FabricanteNeumaticoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo fabricante de neumáticos"
)
async def crear_fabricante(
    fabricante_in: FabricanteNeumaticoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crea un nuevo registro de fabricante de neumáticos."""
    try:
        # Validar nombre duplicado usando el CRUD
        existing_fabricante_nombre = await crud_fabricante.get_by_name(session, name=fabricante_in.nombre)
        if existing_fabricante_nombre:
            logger.warning(f"Intento de crear fabricante con nombre duplicado: {fabricante_in.nombre}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un fabricante con el nombre '{fabricante_in.nombre}'"
            )

        # Validar código abreviado duplicado usando el CRUD
        if fabricante_in.codigo_abreviado:
            existing_fabricante_codigo = await crud_fabricante.get_by_codigo_abreviado(session, codigo_abreviado=fabricante_in.codigo_abreviado)
            if existing_fabricante_codigo:
                logger.warning(f"Intento de crear fabricante con código duplicado: {fabricante_in.codigo_abreviado}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un fabricante con el código '{fabricante_in.codigo_abreviado}'"
                )

        # Crear el fabricante usando el CRUD
        # Añadir el usuario creador antes de pasar al CRUD si el CRUD base no lo maneja
        fabricante_data = fabricante_in.model_dump()
        fabricante_data['creado_por'] = current_user.id
        
        # El CRUD base maneja la adición, commit y refresh
        db_fabricante = await crud_fabricante.create(session, obj_in=fabricante_in) # Pasar el schema directamente
        logger.info(f"Fabricante '{db_fabricante.nombre}' creado por {current_user.username}")
        
        # Convertir explícitamente a diccionario con los campos necesarios para FabricanteNeumaticoRead
        fabricante_dict = {
            "id": str(db_fabricante.id),
            "nombre": db_fabricante.nombre,
            "codigo_abreviado": db_fabricante.codigo_abreviado,
            "activo": db_fabricante.activo,
            "creado_en": db_fabricante.creado_en,
            "actualizado_en": db_fabricante.actualizado_en
        }
        
        return fabricante_dict
    except IntegrityError as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.warning(f"Error de integridad al crear fabricante (posible duplicado BD): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al guardar. El nombre o código ya podría existir (verificar mayúsculas/acentos si aplica) o hubo otro problema."
        )
    except Exception as e:
         # El CRUD base ya hizo rollback si falló el commit
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
    if activo is True:
        # Usar el método específico para activos
        fabricantes = await crud_fabricante.get_multi_active(session, skip=skip, limit=limit)
    elif activo is False:
        # Si se pide inactivos, necesitamos un método específico o filtrar aquí
        # Por ahora, obtendremos todos y filtraremos (menos eficiente para grandes datasets)
        # O mejor, añadimos un método get_multi_inactive al CRUD si es necesario frecuentemente
        # Para simplificar, usaremos get_multi y filtraremos si activo is False
        all_fabricantes = await crud_fabricante.get_multi(session, skip=skip, limit=limit)
        fabricantes = [f for f in all_fabricantes if not f.activo]
    else: # activo is None (obtener todos)
        fabricantes = await crud_fabricante.get_multi(session, skip=skip, limit=limit)

    # Nota: La ordenación por nombre no está en el CRUD base get_multi.
    # Si la ordenación es crucial, se debe añadir al método CRUD o manejar aquí.
    # Por ahora, devolvemos como vienen del CRUD base/filtrado.
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
    # Usar el método get del CRUD
    db_fabricante = await crud_fabricante.get(session, id=fabricante_id)
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
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Actualiza los datos de un fabricante existente."""
    try:
        # Obtener el fabricante usando el CRUD
        db_fabricante = await crud_fabricante.get(session, id=fabricante_id)
        if not db_fabricante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fabricante con ID {fabricante_id} no encontrado para actualizar."
            )

        update_data = fabricante_update.model_dump(exclude_unset=True)

        # Validar nombre duplicado (si se está actualizando el nombre)
        if "nombre" in update_data and update_data["nombre"] != db_fabricante.nombre:
            existing_fabricante_nombre = await crud_fabricante.get_by_name(session, name=update_data["nombre"])
            if existing_fabricante_nombre and str(existing_fabricante_nombre.id) != str(fabricante_id):
                logger.warning(f"Intento de actualizar fabricante {fabricante_id} con nombre duplicado: {update_data['nombre']}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail=f"Nombre '{update_data['nombre']}' ya existe."
                )

        # Validar código abreviado duplicado (si se está actualizando el código)
        if "codigo_abreviado" in update_data and update_data["codigo_abreviado"] != db_fabricante.codigo_abreviado:
            if update_data["codigo_abreviado"]:
                existing_fabricante_codigo = await crud_fabricante.get_by_codigo_abreviado(session, codigo_abreviado=update_data["codigo_abreviado"])
                if existing_fabricante_codigo and str(existing_fabricante_codigo.id) != str(fabricante_id):
                    logger.warning(f"Intento de actualizar fabricante {fabricante_id} con código duplicado: {update_data['codigo_abreviado']}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT, 
                        detail=f"Código '{update_data['codigo_abreviado']}' ya existe."
                    )

        # Añadir usuario actualizador antes de pasar al CRUD si el CRUD base no lo maneja
        update_data['actualizado_en'] = datetime.now(timezone.utc)
        update_data['actualizado_por'] = current_user.id

        # Actualizar el fabricante usando el CRUD
        db_fabricante = await crud_fabricante.update(session, db_obj=db_fabricante, obj_in=update_data) # Pasar el diccionario de actualización
        logger.info(f"Fabricante {fabricante_id} actualizado por {current_user.username}")
        
        # Convertir explícitamente a diccionario con los campos necesarios para FabricanteNeumaticoRead
        fabricante_dict = {
            "id": str(db_fabricante.id),
            "nombre": db_fabricante.nombre,
            "codigo_abreviado": db_fabricante.codigo_abreviado,
            "activo": db_fabricante.activo,
            "creado_en": db_fabricante.creado_en,
            "actualizado_en": db_fabricante.actualizado_en
        }
        
        return fabricante_dict
    except IntegrityError as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.warning(f"Error de integridad al actualizar fabricante {fabricante_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al guardar. El nombre o código ya podría existir o hubo otro problema."
        )
    except Exception as e:
        # El CRUD base ya hizo rollback si falló el commit
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
    current_user: Usuario = Depends(get_current_active_user) # Usar la dependencia centralizada
):
    """Marca un fabricante como inactivo."""
    # Obtener el fabricante usando el CRUD
    db_fabricante = await crud_fabricante.get(session, id=fabricante_id)
    if not db_fabricante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fabricante con ID {fabricante_id} no encontrado para desactivar."
        )

    if not db_fabricante.activo:
        # Si ya está inactivo, no hacemos nada y devolvemos 204
        return

    # Actualizar el estado activo a False usando el método update del CRUD
    # Pasamos un diccionario con solo el campo a actualizar
    update_data = {
        "activo": False,
        "actualizado_en": datetime.now(timezone.utc),
        "actualizado_por": current_user.id
    }
    try:
        await crud_fabricante.update(session, db_obj=db_fabricante, obj_in=update_data)
        logger.info(f"Fabricante {fabricante_id} desactivado por {current_user.username}")
        # No es necesario devolver el objeto para 204 NO CONTENT
    except Exception as e:
        # El CRUD base ya hizo rollback si falló el commit
        logger.error(f"Error al desactivar fabricante {fabricante_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al desactivar el fabricante."
        )

