# ges_neu_api/catalogos/crud.py

from typing import Any, Dict, Optional, Union, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import TypeDecorator

# Importar modelos y esquemas locales
from . import models, schemas

class UUIDType(TypeDecorator):
    impl = PGUUID
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(UUID())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            raise NotImplementedError("Only PostgreSQL is supported")

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return UUID(value)

# --- CRUD para Fabricante ---

async def get_fabricante(db: AsyncSession, fabricante_id: UUID) -> Optional[models.Fabricante]:
    """Obtiene un fabricante por su ID."""
    result = await db.execute(
        select(models.Fabricante).where(models.Fabricante.id == fabricante_id)
    )
    return result.scalars().first()

async def get_all_fabricantes(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    activo: Optional[bool] = None
) -> List[models.Fabricante]:
    """Obtiene todos los fabricantes con filtro opcional por estado activo."""
    query = select(models.Fabricante)
    
    if activo is not None:
        query = query.where(models.Fabricante.activo == activo)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_fabricante(
    db: AsyncSession, 
    *, 
    obj_in: schemas.FabricanteCreate, 
    user_id: UUID
) -> models.Fabricante:
    """Crea un nuevo fabricante."""
    db_obj_data = obj_in.model_dump(exclude_unset=True)
    db_obj_data['creado_por'] = user_id
    db_obj = models.Fabricante(**db_obj_data)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_fabricante(
    db: AsyncSession, 
    *, 
    db_obj: models.Fabricante, 
    obj_in: Union[schemas.FabricanteUpdate, Dict[str, Any]], 
    user_id: UUID
) -> models.Fabricante:
    """Actualiza un fabricante."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Actualizar campos de auditoría
    update_data["actualizado_por"] = user_id
    update_data["actualizado_en"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_fabricante(db: AsyncSession, *, db_obj: models.Fabricante) -> models.Fabricante:
    """Elimina un fabricante."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj

# --- CRUD para ModeloNeumatico ---

async def get_modelo(db: AsyncSession, modelo_id: UUID) -> Optional[models.ModeloNeumatico]:
    """Obtiene un modelo por su ID."""
    result = await db.execute(
        select(models.ModeloNeumatico).where(models.ModeloNeumatico.id == modelo_id)
    )
    return result.scalars().first()

async def get_all_modelos(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    activo: Optional[bool] = None,
    fabricante_id: Optional[UUID] = None
) -> List[models.ModeloNeumatico]:
    """Obtiene todos los modelos con filtros opcionales."""
    query = select(models.ModeloNeumatico)
    
    if activo is not None:
        query = query.where(models.ModeloNeumatico.activo == activo)
    if fabricante_id is not None:
        query = query.where(models.ModeloNeumatico.fabricante_id == fabricante_id)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_modelo(
    db: AsyncSession, 
    *, 
    obj_in: schemas.ModeloNeumaticoCreate, 
    user_id: UUID
) -> models.ModeloNeumatico:
    """Crea un nuevo modelo de neumático."""
    db_obj_data = obj_in.model_dump(exclude_unset=True)
    db_obj_data['creado_por'] = user_id
    
    # Asegurar que los campos Decimal se conviertan correctamente
    for field in ['profundidad_original_mm', 'presion_recomendada_psi', 
                 'profundidad_minima_retiro_mm', 'tasa_desgaste_esperada_mm_km',
                 'porcentaje_desgaste_por_vida']:
        if field in db_obj_data and db_obj_data[field] is not None:
            if not isinstance(db_obj_data[field], Decimal):
                db_obj_data[field] = Decimal(str(db_obj_data[field]))
    
    db_obj = models.ModeloNeumatico(**db_obj_data)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_modelo(
    db: AsyncSession, 
    *, 
    db_obj: models.ModeloNeumatico, 
    obj_in: Union[schemas.ModeloNeumaticoUpdate, Dict[str, Any]], 
    user_id: UUID
) -> models.ModeloNeumatico:
    """Actualiza un modelo de neumático."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Actualizar campos de auditoría
    update_data["actualizado_por"] = user_id
    update_data["actualizado_en"] = datetime.utcnow()
    
    # Manejar campos Decimal
    for field in ['profundidad_original_mm', 'presion_recomendada_psi', 
                 'profundidad_minima_retiro_mm', 'tasa_desgaste_esperada_mm_km',
                 'porcentaje_desgaste_por_vida']:
        if field in update_data and update_data[field] is not None:
            if not isinstance(update_data[field], Decimal):
                update_data[field] = Decimal(str(update_data[field]))

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_modelo(db: AsyncSession, *, db_obj: models.ModeloNeumatico) -> models.ModeloNeumatico:
    """Elimina un modelo de neumático."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj

# --- CRUD para Proveedor ---

async def get_proveedor(db: AsyncSession, proveedor_id: UUID) -> Optional[models.Proveedor]:
    """Obtiene un proveedor por su ID."""
    result = await db.execute(
        select(models.Proveedor).where(models.Proveedor.id == proveedor_id)
    )
    return result.scalars().first()

async def get_proveedor_by_ruc(db: AsyncSession, ruc: str) -> Optional[models.Proveedor]:
    """Obtiene un proveedor por su RUC."""
    result = await db.execute(
        select(models.Proveedor).where(models.Proveedor.ruc == ruc)
    )
    return result.scalars().first()

async def get_proveedor_by_email(db: AsyncSession, email: str) -> Optional[models.Proveedor]:
    """Obtiene un proveedor por su email."""
    result = await db.execute(
        select(models.Proveedor).where(models.Proveedor.email == email)
    )
    return result.scalars().first()

async def get_all_proveedores(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    activo: Optional[bool] = None,
    tipo: Optional[str] = None
) -> List[models.Proveedor]:
    """Obtiene todos los proveedores con filtros opcionales."""
    query = select(models.Proveedor)
    
    if activo is not None:
        query = query.where(models.Proveedor.activo == activo)
    if tipo is not None:
        query = query.where(models.Proveedor.tipo == tipo)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_proveedor(
    db: AsyncSession, 
    *, 
    obj_in: schemas.ProveedorCreate, 
    user_id: UUID
) -> models.Proveedor:
    """Crea un nuevo proveedor."""
    db_obj_data = obj_in.model_dump(exclude_unset=True)
    db_obj_data['creado_por'] = user_id
    db_obj = models.Proveedor(**db_obj_data)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_proveedor(
    db: AsyncSession, 
    *, 
    db_obj: models.Proveedor, 
    obj_in: Union[schemas.ProveedorUpdate, Dict[str, Any]], 
    user_id: UUID
) -> models.Proveedor:
    """Actualiza un proveedor existente."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    update_data['actualizado_por'] = user_id
    update_data['actualizado_en'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_proveedor(db: AsyncSession, *, db_obj: models.Proveedor) -> models.Proveedor:
    """Elimina un proveedor."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj

# --- CRUD para MotivoDesecho ---

async def get_motivo_desecho(db: AsyncSession, motivo_id: UUID) -> Optional[models.MotivoDesecho]:
    """Obtiene un motivo de desecho por su ID."""
    result = await db.execute(
        select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
    )
    return result.scalars().first()

async def get_motivo_desecho_by_codigo(db: AsyncSession, codigo: str) -> Optional[models.MotivoDesecho]:
    """Obtiene un motivo de desecho por su código."""
    result = await db.execute(
        select(models.MotivoDesecho).where(models.MotivoDesecho.codigo == codigo)
    )
    return result.scalars().first()

async def get_all_motivos_desecho(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    activo: Optional[bool] = None
) -> List[models.MotivoDesecho]:
    """Obtiene todos los motivos de desecho con filtros opcionales."""
    query = select(models.MotivoDesecho)
    
    if activo is not None:
        query = query.where(models.MotivoDesecho.activo == activo)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_motivo_desecho(
    db: AsyncSession, 
    *, 
    obj_in: schemas.MotivoDesechoCreate, 
    user_id: UUID
) -> models.MotivoDesecho:
    """Crea un nuevo motivo de desecho."""
    db_obj = models.MotivoDesecho(
        **obj_in.model_dump(),
        creado_por=user_id
    )
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_motivo_desecho(
    db: AsyncSession, 
    *, 
    db_obj: models.MotivoDesecho, 
    obj_in: Union[schemas.MotivoDesechoUpdate, Dict[str, Any]], 
    user_id: UUID
) -> models.MotivoDesecho:
    """Actualiza un motivo de desecho existente."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    update_data['actualizado_por'] = user_id
    update_data['actualizado_en'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_motivo_desecho(db: AsyncSession, *, db_obj: models.MotivoDesecho) -> models.MotivoDesecho:
    """Elimina un motivo de desecho."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj

# --- CRUD para Almacen ---

async def get_almacen(
    db: AsyncSession, 
    almacen_id: UUID
) -> Optional[models.Almacen]:
    """Obtiene un almacén por su ID."""
    result = await db.execute(
        select(models.Almacen)
        .where(models.Almacen.id == almacen_id)
    )
    return result.scalar_one_or_none()

async def get_almacen_by_codigo(
    db: AsyncSession, 
    codigo: str
) -> Optional[models.Almacen]:
    """Obtiene un almacén por su código."""
    result = await db.execute(
        select(models.Almacen)
        .where(func.lower(models.Almacen.codigo) == func.lower(codigo))
    )
    return result.scalar_one_or_none()

async def get_all_almacenes(
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
        skip: Número de registros a omitir (para paginación)
        limit: Número máximo de registros a devolver
        activo: Filtrar por estado activo/inactivo
        
    Returns:
        Lista de almacenes
    """
    query = select(models.Almacen).order_by(models.Almacen.nombre)
    
    if activo is not None:
        query = query.where(models.Almacen.activo == activo)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def create_almacen(
    db: AsyncSession, 
    *, 
    almacen_in: schemas.AlmacenCreate, 
    user_id: UUID
) -> models.Almacen:
    """
    Crea un nuevo almacén.
    
    Args:
        db: Sesión de base de datos
        almacen_in: Datos del almacén a crear
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El almacén creado
    """
    db_obj = models.Almacen(
        **almacen_in.model_dump(),
        creado_por=user_id
    )
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_almacen(
    db: AsyncSession, 
    *, 
    db_obj: models.Almacen, 
    almacen_in: schemas.AlmacenUpdate,
    user_id: UUID
) -> models.Almacen:
    """
    Actualiza un almacén existente.
    
    Args:
        db: Sesión de base de datos
        db_obj: Instancia del almacén a actualizar
        almacen_in: Datos a actualizar
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El almacén actualizado
    """
    update_data = almacen_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    # Actualizar campos de auditoría
    db_obj.actualizado_en = datetime.now()
    db_obj.actualizado_por = user_id
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_almacen(
    db: AsyncSession, 
    *, 
    almacen_id: UUID
) -> bool:
    """
    Elimina un almacén por su ID.
    
    Args:
        db: Sesión de base de datos
        almacen_id: ID del almacén a eliminar
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    result = await db.execute(
        delete(models.Almacen)
        .where(models.Almacen.id == almacen_id)
    )
    await db.commit()
    return result.rowcount > 0

# --- CRUD para ParametroInventario ---

async def get_parametro_inventario(
    db: AsyncSession, 
    parametro_id: UUID
) -> Optional[models.ParametroInventario]:
    """Obtiene un parámetro de inventario por su ID."""
    result = await db.execute(
        select(models.ParametroInventario)
        .where(models.ParametroInventario.id == parametro_id)
    )
    return result.scalar_one_or_none()

async def get_parametro_inventario_by_codigo(
    db: AsyncSession, 
    codigo: str
) -> Optional[models.ParametroInventario]:
    """Obtiene un parámetro de inventario por su código."""
    result = await db.execute(
        select(models.ParametroInventario)
        .where(func.lower(models.ParametroInventario.codigo) == func.lower(codigo))
    )
    return result.scalar_one_or_none()

async def get_all_parametros_inventario(
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
        skip: Número de registros a omitir (para paginación)
        limit: Número máximo de registros a devolver
        activo: Filtrar por estado activo/inactivo
        
    Returns:
        Lista de parámetros de inventario
    """
    query = select(models.ParametroInventario).order_by(models.ParametroInventario.nombre)
    
    if activo is not None:
        query = query.where(models.ParametroInventario.activo == activo)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

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
        El parámetro de inventario creado
    """
    db_obj = models.ParametroInventario(
        **parametro_in.model_dump(),
        creado_por=user_id
    )
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_parametro_inventario(
    db: AsyncSession, 
    *, 
    db_obj: models.ParametroInventario, 
    parametro_in: Union[schemas.ParametroInventarioUpdate, Dict[str, Any]],
    user_id: UUID
) -> models.ParametroInventario:
    """
    Actualiza un parámetro de inventario existente.
    
    Args:
        db: Sesión de base de datos
        db_obj: Instancia del parámetro a actualizar
        parametro_in: Datos a actualizar
        user_id: ID del usuario que realiza la operación
        
    Returns:
        El parámetro de inventario actualizado
    """
    if isinstance(parametro_in, dict):
        update_data = parametro_in
    else:
        update_data = parametro_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    # Actualizar campos de auditoría
    db_obj.actualizado_en = datetime.now()
    db_obj.actualizado_por = user_id
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_parametro_inventario(
    db: AsyncSession, 
    *, 
    parametro_id: UUID
) -> bool:
    """
    Elimina un parámetro de inventario por su ID.
    
    Args:
        db: Sesión de base de datos
        parametro_id: ID del parámetro a eliminar
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    result = await db.execute(
        delete(models.ParametroInventario)
        .where(models.ParametroInventario.id == parametro_id)
    )
    await db.commit()
    return result.rowcount > 0
