# ges_neu_api/catalogos/service.py

from uuid import UUID
from typing import List, Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime

# Importaciones locales
from . import crud, models, schemas

# --- Lógica de negocio para Fabricantes ---

async def get_all_fabricantes(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    activo: Optional[bool] = None
) -> List[models.Fabricante]:
    """Obtiene todos los fabricantes con filtro opcional por estado."""
    return await crud.get_all_fabricantes(
        db, skip=skip, limit=limit, activo=activo
    )

async def get_fabricante_by_id(
    db: AsyncSession, 
    fabricante_id: UUID
) -> models.Fabricante:
    """Obtiene un fabricante por ID."""
    db_fabricante = await crud.get_fabricante(db, fabricante_id=fabricante_id)
    if not db_fabricante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Fabricante no encontrado"
        )
    return db_fabricante

async def create_fabricante(
    db: AsyncSession, 
    *, 
    fabricante_in: schemas.FabricanteCreate, 
    user_id: UUID
) -> models.Fabricante:
    """Crea un nuevo fabricante."""
    # Verificar si ya existe un fabricante con el mismo nombre o código
    existing = await db.execute(
        crud.select(models.Fabricante).where(
            (models.Fabricante.nombre == fabricante_in.nombre) |
            (models.Fabricante.codigo_abreviado == fabricante_in.codigo_abreviado)
        )
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un fabricante con este nombre o código"
        )
        
    return await crud.create_fabricante(
        db, obj_in=fabricante_in, user_id=user_id
    )

async def update_fabricante(
    db: AsyncSession, 
    *, 
    fabricante_id: UUID, 
    fabricante_in: schemas.FabricanteUpdate, 
    user_id: UUID
) -> models.Fabricante:
    """Actualiza un fabricante."""
    db_fabricante = await get_fabricante_by_id(db, fabricante_id)
    
    # Verificar unicidad del nombre y código
    if fabricante_in.nombre or fabricante_in.codigo_abreviado:
        existing = await db.execute(
            crud.select(models.Fabricante).where(
                (models.Fabricante.id != fabricante_id) &
                (
                    (models.Fabricante.nombre == fabricante_in.nombre) |
                    (models.Fabricante.codigo_abreviado == fabricante_in.codigo_abreviado)
                )
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro fabricante con este nombre o código"
            )
    
    return await crud.update_fabricante(
        db, db_obj=db_fabricante, obj_in=fabricante_in, user_id=user_id
    )

async def delete_fabricante(
    db: AsyncSession, 
    *, 
    fabricante_id: UUID
) -> models.Fabricante:
    """Elimina un fabricante."""
    db_fabricante = await get_fabricante_by_id(db, fabricante_id)
    
    # Verificar si el fabricante tiene modelos asociados
    modelos = await crud.get_all_modelos(
        db, fabricante_id=fabricante_id, limit=1
    )
    if modelos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un fabricante con modelos asociados"
        )
    
    return await crud.remove_fabricante(db, db_obj=db_fabricante)

# --- Lógica de negocio para Modelos ---

async def get_all_modelos(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    fabricante_id: Optional[UUID] = None,
    activo: Optional[bool] = None
) -> List[models.ModeloNeumatico]:
    """Obtiene todos los modelos con filtros opcionales."""
    return await crud.get_all_modelos(
        db, 
        skip=skip, 
        limit=limit, 
        fabricante_id=fabricante_id,
        activo=activo
    )

async def get_modelo_by_id(
    db: AsyncSession, 
    modelo_id: UUID
) -> models.ModeloNeumatico:
    """Obtiene un modelo por ID."""
    db_modelo = await crud.get_modelo(db, modelo_id=modelo_id)
    if not db_modelo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado"
        )
    return db_modelo

async def create_modelo(
    db: AsyncSession, 
    *, 
    modelo_in: schemas.ModeloNeumaticoCreate, 
    user_id: UUID
) -> models.ModeloNeumatico:
    """Crea un nuevo modelo."""
    # Verificar si el fabricante existe
    fabricante = await crud.get_fabricante(db, fabricante_id=modelo_in.fabricante_id)
    if not fabricante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El fabricante especificado no existe"
        )
    
    # Verificar si ya existe un modelo con el mismo nombre para este fabricante
    existing = await db.execute(
        crud.select(models.ModeloNeumatico).where(
            (models.ModeloNeumatico.fabricante_id == modelo_in.fabricante_id) &
            (models.ModeloNeumatico.nombre_modelo == modelo_in.nombre_modelo)
        )
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un modelo con este nombre para el fabricante"
        )
    
    return await crud.create_modelo(db, obj_in=modelo_in, user_id=user_id)

async def update_modelo(
    db: AsyncSession, 
    *, 
    modelo_id: UUID, 
    modelo_in: schemas.ModeloNeumaticoUpdate, 
    user_id: UUID
) -> models.ModeloNeumatico:
    """Actualiza un modelo."""
    db_modelo = await get_modelo_by_id(db, modelo_id)
    
    # Verificar si se está cambiando el fabricante
    if modelo_in.fabricante_id and modelo_in.fabricante_id != db_modelo.fabricante_id:
        fabricante = await crud.get_fabricante(db, fabricante_id=modelo_in.fabricante_id)
        if not fabricante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El fabricante especificado no existe"
            )
    
    # Verificar unicidad del nombre del modelo para el fabricante
    if modelo_in.nombre_modelo:
        existing = await db.execute(
            crud.select(models.ModeloNeumatico).where(
                (models.ModeloNeumatico.id != modelo_id) &
                (models.ModeloNeumatico.fabricante_id == (modelo_in.fabricante_id or db_modelo.fabricante_id)) &
                (models.ModeloNeumatico.nombre_modelo == modelo_in.nombre_modelo)
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro modelo con este nombre para el fabricante"
            )
    
    return await crud.update_modelo(
        db, db_obj=db_modelo, obj_in=modelo_in, user_id=user_id
    )

async def delete_modelo(
    db: AsyncSession, 
    *, 
    modelo_id: UUID
) -> models.ModeloNeumatico:
    """Elimina un modelo."""
    db_modelo = await get_modelo_by_id(db, modelo_id)
    
    # Aquí podrías agregar validaciones adicionales, como verificar
    # si el modelo está siendo utilizado en neumáticos existentes
    
    return await crud.remove_modelo(db, db_obj=db_modelo)

# --- Lógica de negocio para Proveedores ---

async def get_all_proveedores(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    activo: Optional[bool] = None,
    tipo: Optional[str] = None
) -> List[models.Proveedor]:
    """Obtiene todos los proveedores con filtros opcionales."""
    return await crud.get_all_proveedores(
        db, skip=skip, limit=limit, activo=activo, tipo=tipo
    )

async def get_proveedor_by_id(
    db: AsyncSession, 
    proveedor_id: UUID
) -> models.Proveedor:
    """Obtiene un proveedor por ID."""
    db_proveedor = await crud.get_proveedor(db, proveedor_id=proveedor_id)
    if not db_proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Proveedor no encontrado"
        )
    return db_proveedor

async def create_proveedor(
    db: AsyncSession, 
    *, 
    proveedor_in: schemas.ProveedorCreate, 
    user_id: UUID
) -> models.Proveedor:
    """Crea un nuevo proveedor."""
    # Verificar si ya existe un proveedor con el mismo RUC
    if proveedor_in.ruc:
        existing = await crud.get_proveedor_by_ruc(db, ruc=proveedor_in.ruc)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un proveedor con este RUC"
            )
    
    # Verificar si ya existe un proveedor con el mismo email
    if proveedor_in.email:
        existing = await crud.get_proveedor_by_email(db, email=proveedor_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un proveedor con este email"
            )
    
    return await crud.create_proveedor(db, obj_in=proveedor_in, user_id=user_id)

async def update_proveedor(
    db: AsyncSession, 
    *, 
    proveedor_id: UUID, 
    proveedor_in: schemas.ProveedorUpdate, 
    user_id: UUID
) -> models.Proveedor:
    """Actualiza un proveedor existente."""
    db_proveedor = await get_proveedor_by_id(db, proveedor_id=proveedor_id)
    
    # Verificar unicidad de RUC si se está actualizando
    if proveedor_in.ruc and proveedor_in.ruc != db_proveedor.ruc:
        existing = await crud.get_proveedor_by_ruc(db, ruc=proveedor_in.ruc)
        if existing and existing.id != proveedor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro proveedor con este RUC"
            )
    
    # Verificar unicidad de email si se está actualizando
    if proveedor_in.email and proveedor_in.email != db_proveedor.email:
        existing = await crud.get_proveedor_by_email(db, email=proveedor_in.email)
        if existing and existing.id != proveedor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro proveedor con este email"
            )
    
    return await crud.update_proveedor(
        db, db_obj=db_proveedor, obj_in=proveedor_in, user_id=user_id
    )

async def delete_proveedor(
    db: AsyncSession, 
    *, 
    proveedor_id: UUID
) -> models.Proveedor:
    """Elimina un proveedor."""
    db_proveedor = await get_proveedor_by_id(db, proveedor_id)
    
    # Verificar si el proveedor tiene relaciones que impidan su eliminación
    # (esto es un ejemplo, ajustar según el modelo de datos)
    # if db_proveedor.compras:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="No se puede eliminar un proveedor con compras asociadas"
    #     )
    
    return await crud.remove_proveedor(db, db_obj=db_proveedor)

# --- Lógica de negocio para Motivos de Desecho ---

async def get_all_motivos_desecho(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    activo: Optional[bool] = None
) -> List[models.MotivoDesecho]:
    """
    Obtiene todos los motivos de desecho con filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a omitir (paginación)
        limit: Número máximo de registros a devolver
        activo: Filtrar por estado activo/inactivo
        
    Returns:
        Lista de motivos de desecho
    """
    return await crud.get_all_motivos_desecho(
        db, skip=skip, limit=limit, activo=activo
    )

async def get_motivo_desecho_by_id(
    db: AsyncSession, 
    motivo_id: UUID
) -> models.MotivoDesecho:
    """
    Obtiene un motivo de desecho por su ID.
    
    Args:
        db: Sesión de base de datos
        motivo_id: ID del motivo de desecho
        
    Returns:
        El motivo de desecho solicitado
        
    Raises:
        HTTPException: Si el motivo no se encuentra
    """
    db_motivo = await crud.get_motivo_desecho(db, motivo_id=motivo_id)
    if not db_motivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Motivo de desecho no encontrado"
        )
    return db_motivo

async def create_motivo_desecho(
    db: AsyncSession, 
    *, 
    motivo_in: schemas.MotivoDesechoCreate, 
    user_id: UUID
) -> models.MotivoDesecho:
    """
    Crea un nuevo motivo de desecho.
    
    Args:
        db: Sesión de base de datos
        motivo_in: Datos del motivo de desecho a crear
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El motivo de desecho creado
        
    Raises:
        HTTPException: Si ya existe un motivo con el mismo código
    """
    # Verificar si ya existe un motivo con el mismo código
    existing = await crud.get_motivo_desecho_by_codigo(db, codigo=motivo_in.codigo)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un motivo de desecho con este código"
        )
    
    return await crud.create_motivo_desecho(
        db, obj_in=motivo_in, user_id=user_id
    )

async def update_motivo_desecho(
    db: AsyncSession, 
    *, 
    motivo_id: UUID, 
    motivo_in: Union[schemas.MotivoDesechoUpdate, Dict[str, Any]], 
    user_id: UUID
) -> models.MotivoDesecho:
    """
    Actualiza un motivo de desecho existente.
    
    Args:
        db: Sesión de base de datos
        motivo_id: ID del motivo de desecho a actualizar
        motivo_in: Datos a actualizar
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El motivo de desecho actualizado
        
    Raises:
        HTTPException: Si el motivo no se encuentra o hay un conflicto con el código
    """
    db_motivo = await get_motivo_desecho_by_id(db, motivo_id=motivo_id)
    
    # Verificar unicidad del código si se está actualizando
    if isinstance(motivo_in, dict):
        codigo = motivo_in.get('codigo')
    else:
        codigo = motivo_in.codigo
    
    if codigo and codigo != db_motivo.codigo:
        existing = await crud.get_motivo_desecho_by_codigo(db, codigo=codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro motivo de desecho con este código"
            )
    
    return await crud.update_motivo_desecho(
        db, db_obj=db_motivo, obj_in=motivo_in, user_id=user_id
    )

async def delete_motivo_desecho(
    db: AsyncSession, 
    *, 
    motivo_id: UUID
) -> models.MotivoDesecho:
    """
    Elimina un motivo de desecho.
    
    Args:
        db: Sesión de base de datos
        motivo_id: ID del motivo de desecho a eliminar
        
    Returns:
        El motivo de desecho eliminado
        
    Raises:
        HTTPException: Si el motivo no se encuentra o no se puede eliminar
    """
    db_motivo = await get_motivo_desecho_by_id(db, motivo_id=motivo_id)
    
    # Aquí podrías agregar validaciones adicionales, por ejemplo:
    # - Verificar si hay neumáticos asociados a este motivo de desecho
    # - Verificar si hay registros históricos que lo referencien
    
    return await crud.remove_motivo_desecho(db, db_obj=db_motivo)

# --- Servicios para Almacen ---

async def get_almacen(
    db: AsyncSession,
    almacen_id: UUID
) -> models.Almacen:
    """
    Obtiene un almacén por su ID.
    
    Args:
        db: Sesión de base de datos
        almacen_id: ID del almacén a buscar
        
    Returns:
        El almacén encontrado
        
    Raises:
        HTTPException: Si el almacén no existe
    """
    db_almacen = await crud.get_almacen(db, almacen_id=almacen_id)
    if not db_almacen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Almacén con ID {almacen_id} no encontrado"
        )
    return db_almacen

async def get_almacen_by_codigo(
    db: AsyncSession,
    codigo: str
) -> Optional[models.Almacen]:
    """
    Obtiene un almacén por su código.
    
    Args:
        db: Sesión de base de datos
        codigo: Código del almacén a buscar
        
    Returns:
        El almacén encontrado o None si no existe
    """
    return await crud.get_almacen_by_codigo(db, codigo=codigo)

async def get_almacenes(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
) -> List[models.Almacen]:
    """
    Obtiene una lista de almacenes con paginación y filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a omitir
        limit: Número máximo de registros a devolver
        activo: Filtrar por estado activo/inactivo
        
    Returns:
        Lista de almacenes
    """
    return await crud.get_all_almacenes(
        db,
        skip=skip,
        limit=limit,
        activo=activo
    )

# --- Servicios para ParametroInventario ---

async def get_parametro_inventario(
    db: AsyncSession,
    parametro_id: UUID
) -> models.ParametroInventario:
    """
    Obtiene un parámetro de inventario por su ID.
    
    Args:
        db: Sesión de base de datos
        parametro_id: ID del parámetro a buscar
        
    Returns:
        El parámetro encontrado
        
    Raises:
        HTTPException: Si el parámetro no existe
    """
    db_parametro = await crud.get_parametro_inventario(db, parametro_id=parametro_id)
    if not db_parametro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parámetro de inventario con ID {parametro_id} no encontrado"
        )
    return db_parametro

async def get_parametro_inventario_by_codigo(
    db: AsyncSession,
    codigo: str
) -> Optional[models.ParametroInventario]:
    """
    Obtiene un parámetro de inventario por su código.
    
    Args:
        db: Sesión de base de datos
        codigo: Código del parámetro a buscar
        
    Returns:
        El parámetro encontrado o None si no existe
    """
    return await crud.get_parametro_inventario_by_codigo(db, codigo=codigo)

async def get_parametros_inventario(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
) -> List[models.ParametroInventario]:
    """
    Obtiene una lista de parámetros de inventario con paginación y filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a omitir
        limit: Número máximo de registros a devolver
        activo: Filtrar por estado activo/inactivo
        
    Returns:
        Lista de parámetros de inventario
    """
    return await crud.get_all_parametros_inventario(
        db,
        skip=skip,
        limit=limit,
        activo=activo
    )

async def create_parametro_inventario(
    db: AsyncSession,
    *,
    parametro_in: schemas.ParametroInventarioCreate,
    user_id: UUID
) -> models.ParametroInventario:
    """
    Crea un nuevo parámetro de inventario.
    
    Args:
        db: Sesión de base de datos
        parametro_in: Datos del parámetro a crear
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El parámetro creado
        
    Raises:
        HTTPException: Si ya existe un parámetro con el mismo código
    """
    # Verificar si ya existe un parámetro con el mismo código
    db_parametro = await crud.get_parametro_inventario_by_codigo(db, codigo=parametro_in.codigo)
    if db_parametro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un parámetro con el código: {parametro_in.codigo}"
        )
    
    return await crud.create_parametro_inventario(
        db=db,
        parametro_in=parametro_in,
        user_id=user_id
    )

async def update_parametro_inventario(
    db: AsyncSession,
    *,
    db_parametro: models.ParametroInventario,
    parametro_in: schemas.ParametroInventarioUpdate,
    user_id: UUID
) -> models.ParametroInventario:
    """
    Actualiza un parámetro de inventario existente.
    
    Args:
        db: Sesión de base de datos
        db_parametro: Instancia del parámetro a actualizar
        parametro_in: Datos a actualizar
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El parámetro actualizado
        
    Raises:
        HTTPException: Si ya existe otro parámetro con el mismo código
    """
    update_data = parametro_in.model_dump(exclude_unset=True)
    
    # Verificar si se está cambiando el código
    if 'codigo' in update_data and update_data['codigo'] != db_parametro.codigo:
        # Verificar si ya existe otro parámetro con el nuevo código
        existing_parametro = await crud.get_parametro_inventario_by_codigo(
            db, 
            codigo=update_data['codigo']
        )
        if existing_parametro and existing_parametro.id != db_parametro.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otro parámetro con el código: {update_data['codigo']}"
            )
    
    return await crud.update_parametro_inventario(
        db=db,
        db_obj=db_parametro,
        parametro_in=parametro_in,
        user_id=user_id
    )

async def delete_parametro_inventario(
    db: AsyncSession,
    *,
    db_parametro: models.ParametroInventario,
    user_id: UUID
) -> models.ParametroInventario:
    """
    Elimina un parámetro de inventario.
    
    Args:
        db: Sesión de base de datos
        db_parametro: Instancia del parámetro a eliminar
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El parámetro eliminado
        
    Raises:
        HTTPException: Si el parámetro no se puede eliminar
    """
    # Aquí podrías agregar verificaciones adicionales si es necesario
    # Por ejemplo, verificar si el parámetro está siendo utilizado en algún lugar
    
    # Eliminar el parámetro
    await crud.remove_parametro_inventario(db, parametro_id=db_parametro.id)
    return db_parametro
